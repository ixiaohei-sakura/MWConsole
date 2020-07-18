import fcntl
import select
import time
import threading
from .thread import *
from subprocess import Popen, PIPE
from .server_status import *


class FrontEndServerProcessControl:
    def __init__(self, Mlogger, cmd: str, Monitor=True, ensoc=True, wsoc=None, soc=None) -> None:
        self.start_cmd = cmd
        self.Mlogger = Mlogger
        self.ensoc = ensoc

        self.server_status = ServerStatus.ISTARTING
        self.start()

        if Monitor:
            if cmd.find('migrate'):
                self.Monitor = ProcessMonitor(self, False)
            else:
                self.Monitor = ProcessMonitor(self)
        if ensoc:
            try:
                self.ws_handle = wsoc
                self.soc = soc
            except:
                self.Mlogger.logger(4, '***BIND PORT ERR***', name='SocketServer')
                self.stop()
                raise SystemExit

    @log_call
    def stop(self, func_call=False) -> int:
        """
        当服务器状态为开启时，关闭服务器
        :param func_call: 当为函数调用时，请设置此参数为True
        :return:
        """
        if self.server_status is ServerStatus.ISRUNNING or self.server_status is ServerStatus.ISRESTARTING or self.server_status is ServerStatus.STOPED_by_func_call:
            self.server_status = ServerStatus.ISTOPPING
            self.process.terminate()
            while self.process.poll() is None:
                time.sleep(server.tick)
            self.Mlogger.logger(0, f"Stoped server, return code: {self.process.poll()}", name='STATUS')
            if func_call:
                self.server_status = ServerStatus.STOPED_by_func_call
                try:
                    self.Monitor.stop_monitor()
                except:
                    self.Mlogger.logger(1, "Monitor fail to stop")
                    stop_server(self)
                return self.process.poll()
            self.server_status = ServerStatus.STOPED_by_it_self
            rm_tmp()
            return True
        else:
            self.Mlogger.logger(1, "服务器正在启动，不允许停止")
            return False

    @log_call
    def start(self) -> bool:
        """
        当服务器状态为等待启动或被函数停止时，此函数会启动服务器
        :return:
        """
        if self.server_status is ServerStatus.STOPED_by_func_call or self.server_status is ServerStatus.ISTARTING or self.server_status == ServerStatus.ISRESTARTING:
            if self.__start_popen__(self.start_cmd):
                try:
                    self.Monitor.start_monitor()
                except AttributeError:
                    pass
                self.server_status = ServerStatus.ISRUNNING
            else:
                self.Mlogger.logger(3, "启动失败")
            return True
        self.Mlogger.logger(1, "服务器不能启动超过一次!")

    @log_call
    def restart(self) -> int:
        """
        将服务器状态设置为等待重启，在服务器运行或被函数调用停止时，此函数会停止并重新启动服务器
        :return:
        """
        if self.server_status is ServerStatus.ISRUNNING or self.server_status is ServerStatus.STOPED_by_func_call:
            tmp = self.stop()
            while self.process.poll() is None: time.sleep(server.tick)
            self.server_status = ServerStatus.ISRESTARTING
            return tmp
        self.Mlogger.logger(1, "服务器正在启动中，请稍后再试")

    @log_call
    def restart_program(self, ttw: int):
        """
        将整个程序停止再启动
        :param ttw:
        :return:
        """
        if self.server_status is ServerStatus.ISRUNNING or self.server_status is ServerStatus.STOPED_by_func_call:
            self.Mlogger.logger(0, '===BEGIN TO RESTART===')
            self.Mlogger.logger(0, '所有线程全部退出, 等待主进程停止.')
            self.stop(func_call=True)
            self.Mlogger.logger(0, 'Main Process call to wait {} seconds.'.format(ttw))
            time.sleep(ttw)
            self.Mlogger.logger(0, '======RESTARTING======')

            os.execl(sys.executable, sys.executable, *sys.argv)

    def recv(self) -> str:
        """
        从stdout中读取数据
        :return:
        """
        r = ''
        pr = self.process.stdout
        while True:
            if not select.select([pr], [], [], server.tick)[0]:
                time.sleep(server.tick)
                continue
            r = pr.read()
            return str(r.rstrip(), encoding='UTF-8')
        return str(r.rstrip(), encoding='UTF-8')

    def stderr_recv(self) -> str:
        """
        从stderr中读取数据
        :return:
        """
        r = ''
        pr = self.process.stderr
        while True:
            if not select.select([pr], [], [], server.tick)[0]:
                time.sleep(server.tick)
                continue
            r = pr.read()
            return str(r.rstrip(), encoding='UTF-8')
        return str(r.rstrip(), encoding='UTF-8')

    def send(self, data: str) -> None:
        """
        向服务器的stdin发送数据
        :param data: 要发送的数据，是一个str
        :return:
        """
        self.process.stdin.write(bytes(data, encoding='UTF-8'))
        self.process.stdin.write(b'\r\n')
        self.process.stdin.flush()

    def join(self):
        """
        在服务器运行时，此函数会阻塞
        :return:
        """
        if self.server_status is ServerStatus.ISTARTING or self.server_status is ServerStatus.ISRUNNING:
            try:
                try:
                    self.Monitor.monitor_thread.join()
                except KeyboardInterrupt:
                    stop_server(self)
            except KeyboardInterrupt:
                try:
                    stop_server(self)
                except KeyboardInterrupt:
                    try:
                        stop_server(self)
                    except KeyboardInterrupt:
                        stop_server(self)

    @log_call
    def __start_popen__(self, start_cmd: str) -> bool:
        try:
            self.process = Popen(start_cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, bufsize=0)
            flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
            fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self.Mlogger.logger(0, 'Server Running at PID:' + str(self.process.pid), name='ProcessInfo')
            self.__process_ = self.process
        except:
            return False
        else:
            return True


class ProcessMonitor:
    def __init__(self, Process_I: FrontEndServerProcessControl, info=True):
        self.process_i = Process_I
        self._info = info
        self.err_thread = None
        self.monitor_thread = None
        self.start_monitor()

    def replace_n(self, data):
        if len(data) == 0:
            return data
        for __ in range(100):
            if __ == 0:
                __ = 1
            data = data.replace('\n' * __, '')
        for _ in range(100):
            if _ == 0:
                _ = 1
            data = data.replace('\r' * _, '')
        return self.out(data)

    def out(self, data=""):
        if data.find("background.jpg") >= 0:
            return ""
        if data.find("logo.png") >= 0:
            return ""
        if data.find("HTTP") >= 0:
            return "\033[1;33m" + data + "\033[0m"
        return data

    @log_call
    def monitor(self, _info: bool):
        if _info:
            self.process_i.Mlogger.logger(0, 'Monitor Started', name="Process")
        while self.process_i.process.poll() is None:
            self.process_i.Mlogger.logger(0, self.replace_n(self.process_i.recv()).split("\n"), name="Process")
            time.sleep(server.tick)
        if _info:
            self.process_i.Mlogger.logger(0, 'Monitor Stoped', name="Process")
        return

    @log_call
    def stderr_monitor(self):
        while True:
            self.process_i.Mlogger.logger(1, (self.process_i.process.stderr.read().decode("utf-8")).split("\n"),
                                          name="ProcessWarn")
            time.sleep(server.tick)

    @log_call
    def start_monitor(self):
        _info = self._info
        self.monitor_thread = threading.Thread(target=self.monitor, args=[_info], daemon=True)
        self.monitor_thread.start()
        self.err_thread = threading.Thread(target=self.stderr_monitor, daemon=True)
        self.err_thread.start()

    @log_call
    def stop_monitor(self):
        stop_thread(self.monitor_thread)
        stop_thread(self.err_thread)

    @log_call
    def restart_monitor(self):
        self.stop_monitor()
        self.start_monitor()

    @property
    def alive(self):
        return self.monitor_thread.isAlive()