import socket
import threading
from .server_status import *
from .thread import *

"""加密解密.......草"""


def decrypt_message(data):
    return data


def encryption_message(data):
    return data


class socket_info:
    command = ""
    message = ""
    ping = ""
    time_stamp = 0.000
    full_data = dict
    content = ""
    data_type = ""

    def set_data(self, full_data: dict):
        if type(full_data) != dict:
            raise TypeError(f"AT socket_info in set_data: 错误的输入变量类型: {type(full_data)}")
        self.command = full_data['cmd']
        self.message = full_data['msg']
        self.ping = full_data['ping']
        self.time_stamp = full_data['time']
        self.content = full_data[full_data['type']]
        self.data_type = full_data['type']
        self.full_data = full_data


class funcs_socall:
    def __init__(self):
        self.funcs_list = []
        self.__add_func_to_run(self.rcmd_stop)

    def __add_func_to_run(self, func):
        def func_(info, soc_server):
            t = threading.Thread(target=func, args=[info, soc_server], daemon=True)
            t.start()
            return t

        self.funcs_list.append(func_)

    def rcmd_stop(self, info: socket_info, soc_server):
        if info.command == "":
            pass


class TimeStampErr(SystemError):
    pass


def close(sfd: socket.socket):
    try:
        sfd.shutdown(2)
        sfd.close()
    except:
        pass


class Socket_handle:
    def __init__(self, Mlogger, process):
        self.id_conn_pool = None
        self.Mlogger = Mlogger
        self.process_ = process
        self._load()
        self.init()

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

    def init(self):
        self.socket.bind(self.FULLADDR)
        self.socket.listen(5)
        thread = threading.Thread(target=self.accept_client)
        thread.setDaemon(True)
        thread.start()
        self.Mlogger.logger(0, f"SocketServer已启动, 等待客户端连接, 监听地址为 {self.addr}:{self.port}", name='SocketServer')

    def accept_client(self):
        while True:
            try:
                client, _ = self.socket.accept()
            except Exception as exc:
                self.Mlogger.logger(2, f"错误：等待连接时消息循环出现错误: {exc}")
                return
            thread = threading.Thread(target=self.message_handle, args=[client])
            thread.setDaemon(True)
            thread.start()
            self.s_conn_pool.append(client)
            self.s_thre_pool.append(thread)
            self.s_thre_dict[client] = thread

    def message_handle(self, client: socket.socket):
        """
        套接字消息处理(threading function)
        :param client: 传入的socket对象
        :return: None
        """

        """开始判断，向客户端先发送消息。"""
        try:
            tmp_msg_recv_json = enjson('cmd', 'conn_server')
            client.sendall(tmp_msg_recv_json.JSON)
        except Exception as exc:
            close(client)
            self.Mlogger.logger(1, f"在处理套接字消息时捕获到一个错误，此套接字将会在此停止。错误信息：{exc}")
            return

        """第二次判断, 获取时间戳。"""
        try:
            tmp = dejson(client.recv(1024).decode('utf-8'))
            if tmp.time == tmp_msg_recv_json.time:
                ID = tmp
            else:
                ID = tmp
        except Exception as exc:
            close(client)
            self.Mlogger.logger(1, f"在处理套接字消息时捕获到一个错误，此套接字将会在此停止。错误信息：{exc}")
            return

        """判断用户名"""
        if ID.msgtype != 'id':
            client.sendall(enjson('cmd', 'close_conn'))
            close(client)
            self.Mlogger.logger(1, f"错误的套接字消息类型，应该接受的类型为: 'id' type, 但却收到了意外的消息类型: {ID.msgtype}")
            return
        ID = ID.msg
        """判断用户名合法性"""
        if len(ID) == 0:
            client.sendall(enjson('cmd', 'close_conn'))
            close(client)
            self.Mlogger.logger(1, "错误的用户名，长度为0.")
            return
        else:
            for k in self.id_conn_pool.keys():
                if ID == k:
                    client.sendall(enjson('cmd', 'close_conn'))
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
            client.sendall(enjson('cmd', 'id_ok'))

        """全部判断完毕，登陆完毕，认证完毕，控制台输出有关于socket的info信息，进入消息循环。"""
        self.num_online_client += 1
        self.Mlogger.logger(0, f"当前客户端在线数量: {self.num_online_client}", name='SocketServer')
        self.Mlogger.logger(0, '统计客户端id:', name='SocketServer')
        for value in self.id_conn_pool.keys():
            self.Mlogger.logger(0, f"    -{value}", name='SocketServer')

        """消息循环"""
        while True:
            buff = client.recv(1024).decode('UTF-8')
            """判断消息合法性"""
            if len(buff) == 0:
                try:
                    close(client)
                    self.s_conn_pool.remove(client)
                    del self.s_thre_dict[client]
                    self.num_online_client -= 1
                    self.Mlogger.logger(0, f"当前客户端在线数量: {self.num_online_client}", name='SocketServer')
                    try:
                        del self.id_conn_pool[ID]
                    except Exception as exc:
                        self.Mlogger.logger(1, f"client消息循环/消息处理错误，ID: {ID}, 错误:{exc}, 此消息循环终止，不影响主程序/socket进程")
                        pass
                    self.s_thre_pool.remove(self.s_thre_dict[client])
                except:
                    return
                break
            """解json"""
            tmp = dejson(buff)
            run = funcs_socall()
            info = socket_info()
            server_ = self

            info.set_data(tmp.full)
            for functions in run.funcs_list:
                functions(info, server_)

            # if tmp.msgtype == 'ping' and tmp.msg == 'ping':
            #     client.sendall('pong'.encode('UTF-8'))
            # ##
            # elif tmp.msgtype == 'msg':
            #     self.Mlogger.logger(0, tmp.msg, name='ClientSend')
            # ##
            # elif tmp.msgtype == 'django_info':
            #     self.Mlogger.logger(0, tmp.msg, name='HTTPINFO')
            # ##
            # elif tmp.msgtype == 'cmd':
            #     if tmp.msg == 'stop':
            #         if self.process_.server.stop:
            #             self.Mlogger.logger(0, 'SocketServer会自动停止', name='SocketServer')
            #             value: socket.socket
            #             try:
            #                 client.sendall(enjson('cmd_return', '成功停止服务器'))
            #             except:
            #                 pass
            #             for value in self.s_conn_pool:
            #                 try:
            #                     value.shutdown(2)
            #                     value.close()
            #                 except:
            #                     pass
            #             self.process_.server.restart_flag = True
            #         else:
            #             client.sendall(enjson('cmd_return', '未能成功停止服务器'))
            #     ##
            #     elif tmp.msg == 'reload':
            #         if self.process_.server.restart:
            #             client.sendall(enjson('cmd_return', '成功重载服务器'))
            #         else:
            #             client.sendall(enjson('cmd_return', '未能成功重载服务器'))
            #     ##
            #     else:
            #         client.sendall(enjson('cmd_return', '参数错误'))

    def send_to_all(self, msg: str, _type='msg'):
        for value in self.s_conn_pool:
            value.sendall(enjson(_type, msg))
