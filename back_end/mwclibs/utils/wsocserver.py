import asyncio
import websockets
from .thread import *
from .server_status import *

class WSocket_handle:
    def __init__(self, Mlogger, process):
        self.Mlogger = Mlogger
        self.process = process
        self.client_list = []
        self.client_count = 0
        self.addr = read_config()['WSOCKET']['ADDR']
        self.port = read_config()['WSOCKET']['PORT']
        self.start_ws()

    async def login(self, websocket: websockets.server.WebSocketServerProtocol, path: str):
        await websocket.send(self.enjson('msg', 'conn'))
        while True:
            try:
                recv_text = self.dejson(await websocket.recv())
                response_text = f"your submit context: {recv_text.msg}"
                await websocket.send(self.enjson(recv_text.msgtype, response_text))
            except:
                return

    async def test(self, websocket: websockets.server.WebSocketServerProtocol, path: str):
        await websocket.send(self.enjson('msg', 'conn'))
        while True:
            try:
                recv_text = self.dejson(await websocket.recv())
                response_text = f"your submit context: {recv_text.msg}"
                await websocket.send(self.enjson(recv_text.msgtype, response_text))
            except:
                return

    async def main_logic(self, websocket: websockets.server.WebSocketServerProtocol, path: str):
        self.client_list.append(websocket)
        self.client_count += 1
        self.Mlogger.logger(0, f'GET WEB CONN! online_count: {self.client_count}', name='WSocketServer')
        self.Mlogger.logger(0, f'conn on path: {path}', name='WSocketServer')
        if path != '/':
            try:
                await eval(f'self.{path[1:]}')(websocket, path)
            except Exception as exc:
                await websocket.send(self.enjson('msg', f'No func named: {path[1:]}'))
                await websocket.send(str(exc))
                await websocket.close(reason=f'No Func named: {path[1:]}')
                self.Mlogger.logger(2, f'No Func named: {path[1:]}')
        else:
            await self.login(websocket, path)
        self.client_count -= 1
        self.Mlogger.logger(0, f'OFFINE online_count: {self.client_count}', name='WSocketServer')
        self.client_list.remove(websocket)

    def init(self, e_loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(e_loop)
        self.start_server = websockets.serve(self.main_logic, self.addr, self.port)
        self.serve_async = asyncio.get_event_loop()
        self.serve_async.run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    def start_ws(self):
        try:
            self.serve_async = asyncio.new_event_loop()
            self.serve_thread = threading.Thread(target=self.init, args=[self.serve_async])
            self.serve_thread.setDaemon(True)
            self.serve_thread.start()
            self.Mlogger.logger(0, f'WSocketServer已启动, 等待网页端上线, 监听地址为 {self.addr}:{self.port}', name='WSocketServer')
        except:
            pass

    def stop_ws(self):
        for value in self.client_list:
            value.close()
        self.client_list = []
        try:
            self.start_server.ws_server.close()
        except:
            pass
        try:
            self.serve_async.close()
        except:
            pass
        try:
            stop_thread(self.serve_thread)
        except:
            pass

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

        return _return

    def enjson(self, _type: str, value: str) -> str:
        tmp = {"ping": "", "cmd": "", "cmd_return": "", 'type': _type, _type: value}
        return json.dumps(tmp)
