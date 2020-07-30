import fcntl
import os
import select
import time
import sys
import threading
import logging
import re
import socket
import json

from logging.handlers import TimedRotatingFileHandler
from subprocess import PIPE, Popen

class MwebLogger():
    def __init__(self: classmethod, name='mwc-httpserver'):
        self.name = name
        self._logger = self._setup_log_file(name)

    def _get_time(self: classmethod) -> str:
        return time.strftime("%H:%M:%S", time.localtime())

    def _setup_log_file(self: classmethod, name: str):
        logger = logging.getLogger(name)
        if os.path.isdir('./log') is not True:
            os.mkdir('./log')
        log_path = './log/latest.log'
        logger.setLevel(logging.INFO)
        file_handler = TimedRotatingFileHandler(filename=log_path, when="MIDNIGHT", interval=1, backupCount=30)
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(module)s.%(funcName)s(%(filename)s:%(lineno)d)][%(process)d][%(levelname)s]:%(message)s"))
        logger.addHandler(file_handler)
        return logger

    def logger(self: classmethod, level: int, data: str, name='Main'):
        now_time = self._get_time()
        if len(data) == 0:
            return
        for i in range(100):
            if i == 0: i = 1
            data = data.replace('\n'*i, '')
        for i in range(100):
            if i == 0: i = 1
            data = data.replace('\r'*i, '')
        if level == 0:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;32mInfo\033[0m]: {data}')
            self._logger.info(data)
        elif level == 1:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;33mWarn\033[0m]: {data}')
            self._logger.warn(data)
        elif level == 2:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mError\033[0m]: {data}')
            self._logger.error(data)
        elif level == 3:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;33mDebug\033[0m]: {data}')
            self._logger.debug(data)
        elif level == 4:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mCRITICAL\033[0m]: {data}')
            self._logger.critical(data)

class Socket_handle():
    def __init__(self: classmethod, Mlogger: MwebLogger, process):
        self.Mlogger = Mlogger
        self.process = process
        self.online_client: list
        self.num_online_client: int
        self.addr: str
        self.port: int
        self.FULLADDR: tuple
        self.socket: socket.socket
        self.s_conn_pool: list
        self.s_thre_pool: list
        self.s_thre_dict: dict
        self.accept_thread: threading.Thread
        self._unload()
        self._load()
        self.init()
        super().__init__()

    def _load(self: classmethod):
        self.num_online_client = 0
        self.addr = self._read_config()['SOCKET']['ADDR']
        self.port = self._read_config()['SOCKET']['PORT']
        self.FULLADDR = (self.addr, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_conn_pool = []
        self.s_thre_pool = []
        self.online_client = []
        self.s_thre_dict = {}

    def _unload(self: classmethod):
        self.addr = None
        self.port = None
        self.FULLADDR = None
        self.socket = None
        self.s_conn_pool = None
        self.s_thre_pool = None
        self.s_thre_dict = None
        self.num_online_client = None
        self.online_client = None
        self.addr: str
        self.port: int
        self.FULLADDR: tuple
        self.socket: socket.socket
        self.s_conn_pool: list
        self.s_thre_pool: list
        self.num_online_client: int
        self.online_client: list
        self.s_thre_dict: dict

    def init(self: classmethod):
        self.socket.bind(self.FULLADDR)
        self.socket.listen(5)
        thread = threading.Thread(target=self.accept_client)
        thread.setDaemon(True)
        thread.start()
        self.Mlogger.logger(0, "服务端已启动, 等待客户端连接", name='SocketServer')

    def accept_client(self: classmethod):
        while True:
            client, _ = self.socket.accept()
            thread = threading.Thread(target=self.message_handle, args=[client])
            thread.setDaemon(True)
            thread.start()
            self.s_conn_pool.append(client)
            self.s_thre_pool.append(thread)
            self.s_thre_dict[client] = thread
    
    def message_handle(self: classmethod, client: socket.socket):
        client.sendall(self.send_json('msg', 'conn_server'))
        while True:
            buff = client.recv(1024).decode('UTF-8')
            if len(buff) == 0:
                client.close()
                self.s_thre_pool.remove(self.s_thre_dict[client])
                self.s_conn_pool.remove(client)
                del self.s_thre_dict[client]
                self.Mlogger.logger(0, "有一个客户端下线了", name='SocketServer')
                break
            tmp = self.get_json(buff)
            if tmp.msgtype == 'ping' and tmp.msg == 'ping':
                client.sendall('pong'.encode('UTF-8'))
                self.Mlogger.logger(0, '向客户端返回了pong', name='SocketServer')
            elif tmp.msgtype == 'msg':
                self.Mlogger.logger(0, tmp.msg, name='ClientSend')
            elif tmp.msgtype == 'cmd':
                if tmp.msg == 'stop':
                    if self.process.stop:
                        client.sendall(self.send_json('cmd_return', '成功停止服务器'))
                        self.Mlogger.logger(0, 'SocketServer会自动停止', name='SocketServer')
                    else:
                        client.sendall(self.send_json('cmd_return', '未能成功停止服务器'))
                elif tmp.msg == 'reload':
                    if self.process.restart:
                        client.sendall(self.send_json('cmd_return', '成功重载服务器'))
                    else:
                        client.sendall(self.send_json('cmd_return', '未能成功重载服务器'))
                else:
                    client.sendall(self.send_json('cmd_return', '参数错误'))

    def get_json(self: classmethod, msg: str):
        buff = json.loads(msg)
        try:
            self.Mlogger.logger(0, '客户端消息: {0}, 类型: {1}'.format(buff[buff['type']], buff['type']), name='SocketServer')
        except:
            buff = json.loads(buff)
            self.Mlogger.logger(0, '客户端消息: {0}, 类型: {1}'.format(buff[buff['type']], buff['type']), name='SocketServer')
        class _return:
            msgtype = buff['type']
            msg = buff[buff['type']]
        return _return

    def send_json(self: classmethod, _type: str, value: str):
        tmp = {
            "type":"",
            "ping":"",
            "cmd":"",
            "cmd_return":""
        }
        tmp['type'] = _type
        tmp[_type] = value
        return bytes(json.dumps(tmp), encoding='UTF-8')

    def _write_config(self: classmethod, adict: dict):
        with open('./configs/config.json', 'w') as target:
            target.write(json.dumps(adict))

    def _read_config(self: classmethod) -> dict:
        with open('./configs/config.json', 'r') as target:
            tmp = target.read()
        return json.loads(tmp)

class Start_Interface(): # Socket_handle
    def __init__(self: classmethod, Mlogger: classmethod, cmd: str, Monitor=True, ensoc=True) -> None:
        self.check_config()
        self.start_cmd = cmd
        self.Mlogger = Mlogger
        self.ensoc = ensoc
        self.process: Popen
        self.start_popen(self.start_cmd)
        if Monitor:
            self.Monitor = ProcessMonitor(self)
        if ensoc:
            try:
                self.soc = Socket_handle(self.Mlogger ,self)
            except:
                self.Mlogger.logger(4, '***BIND PORT ERR***', name='SocketServer')
                self.stop()
                raise SystemExit

    def start_popen(self: classmethod, start_cmd: str) -> bool:
        try:
            self.process = Popen(start_cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, bufsize=0)
            flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
            fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self.Mlogger.logger(0, 'Server Running at PID:'+str(self.process.pid))
            self.process_ = self.process
        except:
            return False
        else:
            return True

    def check_config(self: classmethod):
        if os.path.isfile('./configs/config.json') is not True:
            with open('./configs/config.json', 'w') as f:
                tmp = {"ALLOWED_HOSTS": [],"LANGUAGE_CODE": "en-us","TIME_ZONE": "UTC","STATIC_URL": "/static/","ROOT_URLCONF": "mwc-httpserver.urls","SECRET_KEY": "=&=^c#s^lm*#fsxw=odr7&t7!&6m&76si+=f@cx8kc@krrgw!-","WSGI_APPLICATION": "mwc-httpserver.wsgi.application","USE_I18N": True,"USE_L10N": True,"USE_TZ": True,"DEBUG": True,"SOCKET": {"ADDR": "127.0.0.1","PORT": "3547"}}
                JSON = json.dumps(tmp, indent=3)
                f.write(JSON)

    def stop(self: classmethod) -> int:
        if self.process.poll() is None:
            self.process.terminate()
            while self.process.poll() == None:pass
            self.Mlogger.logger(0, f"Stoped server, return code: {self.process.poll()}")
            return True
        else:
            return False

    def start(self: classmethod) -> bool:
        if self.process.poll() != None:
            self.start_popen(self.start_cmd)
            return True

    def restart(self: classmethod) -> bool:
        global process
        self.stop()
        while self.process.poll() == None:pass
        

    def recv(self: classmethod) -> str:
        r = ''
        pr = self.process.stdout
        while True:
            if not select.select([pr], [], [], 0.1)[0]:
                time.sleep(0.1)
                continue
            r = pr.read()
            return str(r.rstrip(), encoding='UTF-8')
        return str(r.rstrip(), encoding='UTF-8')

    def send(self: classmethod, data: str) -> None:
        self.process.stdin.write(bytes(data, encoding='UTF-8'))
        self.process.stdin.write(b'\r\n')
        self.process.stdin.flush()

    def join(self: classmethod):
        try:
            self.Monitor.monitor_thread.join()
        except KeyboardInterrupt:
            try:
                print('')
                self.Mlogger.logger(0, 'STOPPING')
                self.stop()
                self.Monitor.stop_monitor()
                self.Mlogger.logger(0, 'Socket服务端会自动停止')
            except KeyboardInterrupt:
                try:
                    self.stop()
                    self.Monitor.stop_monitor() 
                    self.Mlogger.logger(0, 'Socket服务端会自动停止')
                except KeyboardInterrupt:
                    self.stop()
                    self.Monitor.stop_monitor() 
                    self.Mlogger.logger(0, 'Socket服务端会自动停止')

class ProcessMonitor():
    def __init__(self: classmethod, Process_I: Start_Interface):
        self.process_i = Process_I
        self.thread: threading.Thread
        self.start_monitor()

    def monitor(self: classmethod):
        self.process_i.Mlogger.logger(0, 'Monitor Started')
        while self.process_i.server.poll() is None:
            self.process_i.Mlogger.logger(0, self.process_i.stdout_recv())
        self.process_i.Mlogger.logger(0, 'Monitor Stoped')
        return

    def alive(self: classmethod):
        return self.thread.isAlive()

    def start_monitor(self: classmethod):
        self.thread = threading.Thread(target=self.monitor)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_monitor(self: classmethod):
        self.thread.join(0)

    def restart_monitor(self: classmethod):
        self.stop_monitor()
        self.start_monitor()

class Server_Control():
    def __init__(self):
        self.Mlogger = MwebLogger()
        self.Mlogger.logger(0, 'Checking DataBase')
        Start_Interface(self.Mlogger, 'python3 manage.py migrate', self.read_config()['DEBUG'], ensoc=False).join()
        self.process = Start_Interface(self.Mlogger, 'python3 manage.py runserver 0:880', True)

    def read_config(self: classmethod) -> dict:
        try:
            f = open('./configs/config.json', 'r')
        except:
            pass
        else:
            JSON = json.loads(f.read())
            return JSON