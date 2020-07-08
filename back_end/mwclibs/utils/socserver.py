import socket
import json
import threading
from .server_status import *


class Socket_handle:
    def __init__(self, Mlogger, process):
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

    def _load(self):
        self.num_online_client = 0
        self.addr = read_config()['SOCKET']['ADDR']
        self.port = read_config()['SOCKET']['PORT']
        self.FULLADDR = (self.addr, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_conn_pool = []
        self.s_thre_pool = []
        self.online_client = []
        self.s_thre_dict = {}

    def _unload(self):
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

    def init(self):
        self.socket.bind(self.FULLADDR)
        self.socket.listen(5)
        thread = threading.Thread(target=self.accept_client)
        thread.setDaemon(True)
        thread.start()
        self.Mlogger.logger(0, "SocketServer已启动, 等待客户端连接", name='SocketServer')

    def accept_client(self):
        while True:
            try:
                client, _ = self.socket.accept()
            except:
                return
            thread = threading.Thread(target=self.message_handle, args=[client])
            thread.setDaemon(True)
            thread.start()
            self.s_conn_pool.append(client)
            self.s_thre_pool.append(thread)
            self.s_thre_dict[client] = thread

    def message_handle(self, client: socket.socket):
        try:
            client.sendall(self.enjson('msg', 'conn_server'))
        except:
            return
        try:
            ID = self.dejson(client.recv(1024).decode('utf-8'))
        except:
            try:
                client.shutdown(2)
                client.close()
                return
            except:
                return
        if ID.msgtype != 'id':
            client.sendall(self.enjson('cmd', 'close_conn'))
            try:
                client.shutdown(2)
                client.close()
            except:
                pass
        ID = ID.msg
        if len(ID) == 0:
            client.sendall(self.enjson('cmd', 'close_conn'))
            try:
                client.shutdown(2)
                client.close()
            except:
                pass
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
                    try:
                        del self.id_conn_pool[ID]
                    except:
                        pass
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
                    try:
                        del self.id_conn_pool[ID]
                    except:
                        pass
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
                    if self.process_.server.stop:
                        self.Mlogger.logger(0, 'SocketServer会自动停止', name='SocketServer')
                        value: socket.socket
                        try:
                            client.sendall(self.enjson('cmd_return', '成功停止服务器'))
                        except:
                            pass
                        for value in self.s_conn_pool:
                            try:
                                value.shutdown(2)
                                value.close()
                            except:
                                pass
                        self.process_.server.restart_flag = True
                    else:
                        client.sendall(self.enjson('cmd_return', '未能成功停止服务器'))
                ##
                elif tmp.msg == 'reload':
                    if self.process_.server.restart == True:
                        client.sendall(self.enjson('cmd_return', '成功重载服务器'))
                    else:
                        client.sendall(self.enjson('cmd_return', '未能成功重载服务器'))
                ##
                else:
                    client.sendall(self.enjson('cmd_return', '参数错误'))

    def send_to_all(self, msg: str, _type='msg'):
        for value in self.s_conn_pool:
            value.sendall(self.enjson(_type, msg))

    def dejson(self, msg: str):
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

    def enjson(self, _type: str, value: str):
        tmp = {'type': _type, _type: value}
        return bytes(json.dumps(tmp), encoding='UTF-8')

    def _write_config(self, adict: dict):
        with open('./configs/config.json', 'w') as target:
            target.write(json.dumps(adict))

    def _read_config(self) -> dict:
        with open('./configs/config.json', 'r') as target:
            tmp = target.read()
        return json.loads(tmp)
