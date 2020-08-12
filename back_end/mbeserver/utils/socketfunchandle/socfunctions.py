import threading
from socket import socket


class funcs_socall:
    def __init__(self):
        self.funcs_list = []
        self.__add_func_to_run(self.rmessage)
        self.__add_func_to_run(self.rping)
        self.__add_func_to_run(self.rcmd_stop)
        self.__add_func_to_run(self.rcmd_reload)
        self.__add_func_to_run(self.rcmd_restart_all)

    def __add_func_to_run(self, func):
        def func_(info, server, client, ID):
            t = threading.Thread(target=func, args=[info, server, client, ID], daemon=True)
            t.start()
            return t

        self.funcs_list.append(func_)

    def rmessage(self, info, server, client: socket, ID: str):
        if len(info.message) != 0:
            server.Mlogger.logger(0, info.message, "SocketServer")

    def rping(self, info, server, client: socket, ID: str):
        if info.ping == "ping":
            server.send("ping", "pong", client)

    def rcmd_stop(self, info, server, client: socket, ID: str):
        if info.command == "stop":
            server.Mlogger.logger(0, f"客户端「{ID}」调用stop.")
            server.Mlogger.logger(0, 'SocketServer会自动停止', name='SocketServer')
            server.send("cmd_return", "成功停止[MWC]服务器.", client)
            for value in server.s_conn_pool:
                server.send("cmd", "server_is_stopping", client)
                server.close_conn(value)
            server.MainThread.stop()

    def rcmd_reload(self, info, server, client: socket, ID: str):
        if info.command == "reload":
            server.Mlogger.logger(0, f"客户端「{ID}」调用重载服务器.")
            server.send("cmd_return", "已重载服务器", client)
            server.MainThread.restart()

    def rcmd_restart_all(self, info, server, client: socket, ID: str):
        if info.command == "restart":
            server.Mlogger.logger(0, f"客户端「{ID}」调用重启服务器.")
            server.send("cmd_return", "正在重启服务器", client)
            for value in server.s_conn_pool:
                server.send("cmd", "server_is_restarting", client)
                server.close_conn(value)
