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
import asyncio
import websockets
import platform

from logging.handlers import TimedRotatingFileHandler
from subprocess import PIPE, Popen



class MwebLogger():
    def __init__(self: classmethod, name='MWC'):
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

    def logger(self: classmethod, level: int, data: str, name='Main', end='\n'):
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
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;32mINFO\033[0m]: {data}', end=end)
            self._logger.info(data)
        elif level == 1:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;33mWARN\033[0m]: {data}', end=end)
            self._logger.warn(data)
        elif level == 2:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mERROR\033[0m]: {data}', end=end)
            self._logger.error(data)
        elif level == 3:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;33mDEBUG\033[0m]: {data}', end=end)
            self._logger.debug(data)
        elif level == 4:
            print(f'[\033[1;32m{self.name}\033[0m][{now_time}][{name}/\033[1;31mCRITICAL\033[0m]: {data}', end=end)
            self._logger.critical(data)



class Socket_handle():
    def __init__(self: classmethod, Mlogger: MwebLogger, process):
        self.Mlogger = Mlogger
        self.process_ = process
        self.num_online_client: int
        self.addr: str
        self.port: int
        self.FULLADDR: tuple
        self.socket: socket.socket
        self.s_conn_pool: list
        self.s_thre_pool: list
        self.s_thre_dict: dict
        self.id_conn_pool = {}
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
        self.Mlogger.logger(0, "SocketServer已启动, 等待客户端连接", name='SocketServer')

    def accept_client(self: classmethod):
        while True:
            try:client, _ = self.socket.accept()
            except:return
            thread = threading.Thread(target=self.message_handle, args=[client])
            thread.setDaemon(True)
            thread.start()
            self.s_conn_pool.append(client)
            self.s_thre_pool.append(thread)
            self.s_thre_dict[client] = thread
    
    def message_handle(self: classmethod, client: socket.socket):
        try:
            client.sendall(self.enjson('msg', 'conn_server'))
        except:return
        try:ID = self.dejson(client.recv(1024).decode('utf-8'))
        except:
            try:
                client.shutdown(2)
                client.close()
                return
            except:return
        if ID.msgtype != 'id':
            client.sendall(self.enjson('cmd', 'close_conn'))
            try:
                client.shutdown(2)
                client.close()
            except:pass
        ID = ID.msg
        if len(ID) == 0:
            client.sendall(self.enjson('cmd', 'close_conn'))
            try:
                client.shutdown(2)
                client.close()
            except:pass
        elif ID == 'django_info':
            client.sendall(self.enjson('cmd', 'id_ok'))
        else:
            for k in self.id_conn_pool.keys():
                if ID == k:
                    client.sendall(self.enjson('cmd', 'close_conn'))
                    self.s_conn_pool.remove(client)
                    del self.s_thre_dict[client]
                    self.num_online_client -= 1
                    self.Mlogger.logger(0, f"当前客户端在线数量: {self.num_online_client}", name='SocketServer')
                    try:del self.id_conn_pool[ID]
                    except:pass
                    self.s_thre_pool.remove(self.s_thre_dict[client])
                    return
            self.id_conn_pool[ID] = client
            client.sendall(self.enjson('cmd', 'id_ok'))
        ##
        self.num_online_client += 1
        if not ID.find('django_info'):
            self.Mlogger.logger(0, f"当前客户端在线数量: {self.num_online_client}", name='SocketServer')
            self.Mlogger.logger(0, '统计客户端id:', name='SocketServer')
            for value in self.id_conn_pool.keys():
                self.Mlogger.logger(0, value, name='SocketServer')
        ##
        while True:
            buff = client.recv(1024).decode('UTF-8')
            ##
            if len(buff) == 0:
                try:
                    client.close()
                    self.s_conn_pool.remove(client)
                    del self.s_thre_dict[client]
                    self.num_online_client -= 1
                    if ID != 'django_info':
                        self.Mlogger.logger(0, f"当前客户端在线数量: {self.num_online_client}", name='SocketServer')
                    try:del self.id_conn_pool[ID]
                    except:pass
                    self.s_thre_pool.remove(self.s_thre_dict[client])
                except:
                    return
                break
            ##
            tmp = self.dejson(buff)
            if tmp.msgtype == 'ping' and tmp.msg == 'ping':
                client.sendall('pong'.encode('UTF-8'))
            ##
            elif tmp.msgtype == 'msg':
                self.Mlogger.logger(0, tmp.msg, name='ClientSend')
            ##
            elif tmp.msgtype == 'django_info':
                self.Mlogger.logger(0, tmp.msg, name='HTTPINFO')
            ##
            elif tmp.msgtype == 'cmd':
                if tmp.msg == 'stop':
                    if self.process_.process.stop() == True:
                        self.Mlogger.logger(0, 'SocketServer会自动停止', name='SocketServer')
                        value: socket.socket
                        try:
                            client.sendall(self.enjson('cmd_return', '成功停止服务器'))
                        except:pass
                        for value in self.s_conn_pool:
                            try:
                                value.shutdown(2)
                                value.close()
                            except:pass
                        self.process_.process.restart_flag = True
                    else:
                        client.sendall(self.enjson('cmd_return', '未能成功停止服务器'))
                ##
                elif tmp.msg == 'reload':
                    if self.process_.process.restart() == True:
                        client.sendall(self.enjson('cmd_return', '成功重载服务器'))
                    else:
                        client.sendall(self.enjson('cmd_return', '未能成功重载服务器'))
                ##
                else:
                    client.sendall(self.enjson('cmd_return', '参数错误'))

    def send_to_all(self: classmethod, msg: str, _type='msg'):
        for value in self.s_conn_pool:
            value.sendall(self.enjson(_type, msg))

    def dejson(self: classmethod, msg: str):
        buff = json.loads(msg)
        try:
            if type(buff) == str:
                raise TypeError
        except:
            buff = json.loads(buff)
        class _return:
            msgtype = buff['type']
            msg = buff[buff['type']]
            full = buff
        return _return

    def enjson(self: classmethod, _type: str, value: str):
        tmp = {'type': _type, _type: value}
        return bytes(json.dumps(tmp), encoding='UTF-8')

    def _write_config(self: classmethod, adict: dict):
        with open('./configs/config.json', 'w') as target:
            target.write(json.dumps(adict))

    def _read_config(self: classmethod) -> dict:
        with open('./configs/config.json', 'r') as target:
            tmp = target.read()
        return json.loads(tmp)



class WSocket_handle():
    def __init__(self: classmethod, Mlogger: MwebLogger, process):
        self.Mlogger = Mlogger
        self.process = process
        self.serve_async: asyncio.AbstractEventLoop
        self.serve_thread: threading.Thread
        self.client_list = []
        self.client_count = 0
        self.start_ws()

    async def login(self: classmethod, websocket: websockets.server.WebSocketServerProtocol, path: str):
        await websocket.send(self.enjson('msg', 'conn'))
        while True:
            try:
                recv_text = self.dejson(await websocket.recv())
                response_text = f"your submit context: {recv_text.msg}"
                await websocket.send(self.enjson(recv_text.msgtype, response_text))
            except:
                return

    async def test(self: classmethod, websocket: websockets.server.WebSocketServerProtocol, path: str):
        await websocket.send(self.enjson('msg', 'conn'))
        while True:
            try:
                recv_text = self.dejson(await websocket.recv())
                response_text = f"your submit context: {recv_text.msg}"
                await websocket.send(self.enjson(recv_text.msgtype, response_text))
            except:
                return

    async def main_logic(self: classmethod, websocket: websockets.server.WebSocketServerProtocol, path: str):
        self.client_list.append(websocket)
        self.client_count += 1
        self.Mlogger.logger(0, f'GET WEB CONN! online_count: {self.client_count}', name='WSocketServer')
        self.Mlogger.logger(0, f'conn on path: {path}', name='WSocketServer')
        if path != '/':
            try:
                await eval(f'self.{path[1:]}')(websocket, path)
            except Exception as exc:
                await websocket.send(self.enjson('msg', f'No func named: {path[1:]}'))
                await websocket.send(exc)
                await websocket.close(reason=f'No Func named: {path[1:]}')
                self.Mlogger.logger(2, f'No Func named: {path[1:]}')
        else:
            await self.login(websocket, path)
        self.client_count -= 1
        self.Mlogger.logger(0, f'OFFINE online_count: {self.client_count}', name='WSocketServer')
        self.client_list.remove(websocket)

    def init(self: classmethod, e_loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(e_loop)
        self.start_server = websockets.serve(self.main_logic, self._read_config()['WSOCKET']['ADDR'], self._read_config()['WSOCKET']['PORT'])
        self.serve_async = asyncio.get_event_loop()
        self.serve_async.run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    def start_ws(self: classmethod):
        try:
            self.serve_async = asyncio.new_event_loop()
            self.serve_thread = threading.Thread(target=self.init, args=[self.serve_async])
            self.serve_thread.setDaemon(True)
            self.serve_thread.start()
            self.Mlogger.logger(0, 'WSocketServer已启动, 等待网页端上线', name='WSocketServer')
        except:
            pass

    def stop_ws(self: classmethod):
        for value in self.client_list:
            value.close()
        self.client_list = []
        try:
            self.start_server.ws_server.close()
        except:pass
        try:
            self.serve_async.close()
            self.serve_async.stop()
        except:
            pass
        try:
            self.serve_thread.join(0)
        except:pass

    def _write_config(self: classmethod, adict: dict):
        with open('./configs/config.json', 'w') as target:
            target.write(json.dumps(adict))

    def _read_config(self: classmethod) -> dict:
        with open('./configs/config.json', 'r') as target:
            tmp = target.read()
        return json.loads(tmp)

    def dejson(self: classmethod, msg: str):
        buff = json.loads(msg)
        try:
            if type(buff) == str:
                raise TypeError
        except:
            buff = json.loads(buff)
        class _return:
            msgtype = buff['type']
            msg = buff[buff['type']]
        return _return

    def enjson(self: classmethod, _type: str, value: str) -> str:
        tmp = {
            "type":"",
            "ping":"",
            "cmd":"",
            "cmd_return":""
        }
        tmp['type'] = _type
        tmp[_type] = value
        return json.dumps(tmp)



class Process_Control():
    def __init__(self: classmethod, Mlogger: classmethod, cmd: str, Monitor=True, ensoc=True, wsoc=None, soc=None) -> None:
        self.check_config()
        self.restart_wait_thread: threading.Thread
        self.process: Popen
        self.start_cmd = cmd
        self.Mlogger = Mlogger
        self.ensoc = ensoc
        self.restart_flag = False
        self.start_popen(self.start_cmd)
        if Monitor == True:
            if cmd.find('migrate') == True:
                self.Monitor = ProcessMonitor(self, False)
            else:
                self.Monitor = ProcessMonitor(self)
        if ensoc == True:
            try:
                self.ws_handle: WSocket_handle = wsoc
                self.soc: Socket_handle = soc
            except:
                self.Mlogger.logger(4, '***BIND PORT ERR***', name='SocketServer')
                self.stop()
                raise SystemExit

    def start_popen(self: classmethod, start_cmd: str) -> bool:
        try:
            self.process = Popen(start_cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, bufsize=0)
            flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
            fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self.Mlogger.logger(0, 'Server Running at PID:'+str(self.process.pid), name='ProcessInfo')
            self.process_ = self.process
        except:
            return False
        else:
            return True

    def check_config(self: classmethod):
        if os.path.isfile('./configs/config.json') is not True:
            with open('./configs/config.json', 'w') as f:
                tmp = {"WEBPORT":8000,"PYCMD":"python3","ALLOWED_HOSTS": ["bs.s1.blackserver.cn", "10.168.0.213"],"LANGUAGE_CODE": "en-us","TIME_ZONE": "UTC", "STATIC_URL": "/static/","ROOT_URLCONF": "MwebConsole.urls","SECRET_KEY": "******=&=^c#s^lm*#fBYIXIA@HEIsxwIXiaO@HeiIS%fu&*kingcreatedthis&^#%^@&(*_&*$^$&proJECt#%^&#~!#^#%^@$=f@cx8kc@krrgw!-******","WSGI_APPLICATION": "MwebConsole.wsgi.application","USE_I18N": True,"USE_L10N": True,"USE_TZ": True,"DEBUG": True,"SOCKET": {"ADDR": "127.0.0.1","PORT": 3547},"WSOCKET":{"ADDR": "127.0.0.1","PORT": 3548}}
                JSON = json.dumps(tmp, indent=3)
                f.write(JSON)

    def stop(self: classmethod) -> int:
        if self.process.poll() is None:
            self.process.terminate()
            while self.process.poll() == None:pass
            self.Mlogger.logger(0, f"Stoped server, return code: {self.process.poll()}", name='STATUS')
            return True
        else:
            return False

    def start(self: classmethod) -> bool:
        if self.process.poll() != None:
            self.start_popen(self.start_cmd)
            self.restart_flag = False
            return True

    def restart(self: classmethod) -> bool:
        self.restart_flag = True
        tmp = self.stop()
        while self.process.poll() == None:pass
        return tmp
        
    def _start_wait(self: classmethod):
        if self.restart_flag == True:
            self.Mlogger.logger(0, '等待启动...')
        while self.restart_flag == True:
            pass
        return

    def start_wait(self: classmethod):
        self.restart_wait_thread = threading.Thread(target=self._start_wait)
        self.restart_wait_thread.setDaemon(True)
        self.restart_wait_thread.start()
        self.restart_wait_thread.join()

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
            try:
                self.Monitor.thread.join()
            except KeyboardInterrupt:
                print('')
                self.Mlogger.logger(0, 'STOPPING', name='STATUS')
                self.stop()
                self.Monitor.stop_monitor()
                self.ws_handle.stop_ws()
                self.Mlogger.logger(0, 'Socket服务端会自动停止')
        except KeyboardInterrupt:
            try:
                print('')
                self.Mlogger.logger(0, 'STOPPING', name='STATUS')
                self.stop()
                self.Monitor.stop_monitor()
                self.ws_handle.stop_ws()
                self.Mlogger.logger(0, 'Socket服务端会自动停止')
            except KeyboardInterrupt:
                try:
                    self.stop()
                    self.Monitor.stop_monitor()
                    self.ws_handle.stop_ws()
                    self.Mlogger.logger(0, 'Socket服务端会自动停止')
                except KeyboardInterrupt:
                    self.stop()
                    self.Monitor.stop_monitor()
                    self.ws_handle.stop_ws()
                    self.Mlogger.logger(0, 'Socket服务端会自动停止')



class ProcessMonitor():
    def __init__(self: classmethod, Process_I: Process_Control, info=True):
        self.process_i = Process_I
        self.thread: threading.Thread
        self.start_monitor(_info=info)

    def monitor(self: classmethod, _info: bool):
        if _info == True:
            self.process_i.Mlogger.logger(0, 'Monitor Started', name='Monitor')
        while self.process_i.process.poll() is None:
            self.process_i.Mlogger.logger(0, self.process_i.recv(), name='Monitor')
        if _info == True:
            self.process_i.Mlogger.logger(0, 'Monitor Stoped', name='Monitor')
        return

    def alive(self: classmethod):
        return self.thread.isAlive()

    def start_monitor(self: classmethod, _info: bool):
        self.thread = threading.Thread(target=self.monitor, args=[_info])
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_monitor(self: classmethod):
        self.thread.join(0)

    def restart_monitor(self: classmethod):
        self.stop_monitor()
        self.start_monitor(True)



class Check_Update():
    def __init__(self, SC):
        self.server_control = SC
        self.Mlogger = self.server_control.Mlogger

    def check_version(self: classmethod):
        pass

    def check_update(self: classmethod):
        pass

    def restart_all(self: classmethod, ttw: int):
        self.Mlogger.logger(0, '===BEGIN TO RESTART===')
        self.server_control.process.stop()
        self.server_control.soc_handle.send_to_all('server_restarting', 'server_status')
        self.server_control.ws_handle.stop_ws()
        self.Mlogger.logger(0, '所有线程全部退出, 等待主进程停止.')
        self.Mlogger.logger(0, 'Main Process call to wait {} seconds.'.format(ttw))
        time.sleep(ttw)
        self.Mlogger.logger(0, 'RESTARTING...')

        pythoncmd = sys.executable
        os.execl(pythoncmd, pythoncmd, * sys.argv)



class Server_Control():
    class ConfigFileNotFound(Exception):
        pass

    def __init__(self, argv):
        self.Mlogger = MwebLogger()
        self.init_server()

    def init_server(self: classmethod):
        self.update_checker = Check_Update(self)
        self.msg = """
   __  ____      _____/\\
  /  |/  / | /| / / ___/
 / /|_/ /| |/ |/ / /__  
/ /  /_/ |__/|__/\___/
\/
"""
        for line in self.msg.splitlines():
            self.Mlogger.logger(0, line)
        self.Mlogger.logger(0, '==== MCDRWEBCONSOLE ====')

        time.sleep(0.5)
        self.Mlogger.logger(0, '正在启动MCDR-WEBCONSOLE')
        self.update_checker.check_update()
        self.Mlogger.logger(0, '上报BUG请联系 ixiaohei:')
        self.Mlogger.logger(0, 'QQ: 486118772')
        self.Mlogger.logger(0, 'MwebConsole is OpenSource, find it here:')
        self.Mlogger.logger(0, 'GAYHUB: https://github.com/ixiaohei-sakura/')
        self.Mlogger.logger(0, 'G-PROJECT: https://github.com/ixiaohei-sakura/MWConsole')
        self.Mlogger.logger(0, 'ServerStarted. Quit the server with CONTROL-C')
        time.sleep(3)

        try:
            self.ws_handle = WSocket_handle(self.Mlogger, self)
        except:
            self.Mlogger.logger(4, '***BIND PORT ERR***', name='WSocketServer')
            raise SystemExit

        try:
            self.soc_handle = Socket_handle(self.Mlogger ,self)
        except Exception as exc:
            print(exc)
            self.Mlogger.logger(4, '***BIND PORT ERR***', name='SocketServer')
            raise SystemExit

        self.Mlogger.logger(0, '检查必要的数据表', name='ServerCheck')
        self.__process = Process_Control(self.Mlogger, '{0} manage.py migrate'.format(self.read_config()['PYCMD']), self.read_config()['DEBUG'], ensoc=False)
        self.__process.join()

    def start_all_server(self: classmethod):
         while True:
            self.Mlogger.logger(0, 'StartProcess', name='ProcessServer')
            self.process = Process_Control(self.Mlogger, '{0} manage.py runserver 0:{1}'.format(self.read_config()['PYCMD'], self.read_config()['WEBPORT']), ensoc=True, wsoc=self.ws_handle, soc=self.soc_handle)
            self.process.join()
            if self.process.restart_flag == False:
                break
    
    def read_config(self: classmethod) -> dict:
        try:
            f = open('./configs/config.json', 'r')
        except:
            pass
        else:
            JSON = json.loads(f.read())
            return JSON

try:
    print("init server....")
    process = Server_Control(sys.argv)
except:
    import traceback
    traceback.print_exc()
    input('Fail to initialize Server, press enter to exit.')
else:
    process.start_all_server()



# netstat -anp | grep 880

# python3 manage.py migrate 每当第一次启动时执行此命令.
# python3 manage.py createsuperuser --user hei
# python3 manage.py runserver 0:880



# ADDRESS = ('127.0.0.1', 8712)
 
# g_socket_server = None
# g_conn_pool = []



# init()