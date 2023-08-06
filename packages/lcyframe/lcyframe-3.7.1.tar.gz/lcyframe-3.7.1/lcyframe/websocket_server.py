# coding=utf-8
import sys
import json, logging
import time
from .libs import utils
from .libs.websocket_route import WebSocketRoute
from traceback import format_exc
import asyncio, websockets
from websocket import create_connection
import inspect

"""
pip install websockets
pip install websocket-client
"""
class BaseSocket(object):
    websockets = websockets
    current_event = None
    current_conn = None
    system_uid = None

    def auth(self, conn):
        """
        校验是否合法请求
        """
        if "?" not in conn.path:
            conn.uid = ""
            return None

        path, query_string = conn.path.split("?")
        conf_path, _ = self.path.split("?")
        if path != conf_path:
            return None

        params = {item.split("=")[0]: item.split("=")[1] for item in query_string.split("&") if "=" in item}
        if "token" not in params:
            return None

        uid = params.get("uid", "")
        token = params.get("token", "")

        if token != utils.md5(uid + self.salt):
            return None

        conn.uid = uid
        conn.token = token

        self.add_client(conn)
        return True

    def packing(self, **message):
        """
        默认消息采用json编码
        """
        payload = {}
        __event__ = message.get("__event__")

        if not __event__ and not self.current_event:
            raise Exception("__event__ can not empty value")
        payload["__event__"] = __event__ or self.current_event  # message_handler name by Consumer
        payload["ts"] = int(time.time())
        payload.update(message)
        return json.dumps(payload)

    def send(self, client=None, **message):
        """
        如需要发送给指定的client，则指定client
        """
        if client is None:
            client = self.current_conn
        self.sendall(client, **message)

    def sendall(self, *client, **message):
        """
        send to all client
        默认发送给除自己及系统app以外的客户端连接
        """
        try:
            # 循环发送速度过快，容易造成网络阻塞，导致资源暂满网络缓冲区，可以用背压，没100毫秒发送一批数据
            # for ws in conns:
            #     await ws.send(message)

            # 禁止向app系统连接发送消息
            self.remove_system_client(self.conns)

            # 默认发送给所有连接（不含系统和当前消息发送方)
            if not client:
                clients = list(self.conns.values())
                if self.current_conn in clients:
                    clients.remove(self.current_conn)
            else:
                clients = list(client)

            if clients:
                websockets.broadcast(clients, self.packing(**message))
        except Exception as e:
            logging.warning(format_exc())
            logging.error(str(e))

    def client_key(self, conn):
        return f"{conn.uid}:{conn.id}"

    def add_client(self, conn):
        key = self.client_key(conn)
        if key not in self.conns:
            self.conns[key] = conn

    def remove_client(self, conn):
        key = self.client_key(conn)
        self.conns.pop(key, "")

    def remove_system_client(self, conns):
        keys = []
        for key in list(conns.keys()):
            uid, id = key.split(":")
            if uid != "" and uid in self.system_uid:
                keys.append(key)
        for key in keys:
            self.conns.pop(key, "")

    def inspect_args(self):
        import inspect
        args = inspect.getfullargspec(websockets.serve).args + inspect.getfullargspec(websockets.serve).kwonlyargs
        ws_args = {}
        for k, v in self.websocket_config.items():
            if k in args:
                ws_args[k] = v
        return ws_args

class WebSocketClient(BaseSocket):
    def __init__(self, **kwargs):
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.system_uid = kwargs.get("system_uid", "system")    # 默认系统用户为system
        p = kwargs.pop("path", "")
        self.path = p.split("?")[0] if "?" in p else p
        self.salt = kwargs.pop("salt", "")
        self.token = utils.md5(self.system_uid + self.salt)
        self.protocol = kwargs.get("protocol", "ws")
        self.url = "%s://%s:%s%s?uid=%s&token=%s" % (self.protocol, self.host, self.port, self.path, self.system_uid, self.token)

    def conn(self):
        try:
            self.ws = create_connection(self.url)
        except Exception as e:
            logging.error(format_exc())
            logging.error("websocket connection fail")
        else:
            return self.ws

    def send(self, **message):
        self.conn()
        if self.ws.connected == True:
            self.ws.send(self.packing(**message))
            self.ws.close()
        else:
            logging.error("websocket connection closed")

    async def async_send(self, **message):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(self.packing(**message))

class WebSocketWorker(BaseSocket):
    """
    websocket 服务端
    """
    def __init__(self, **kwargs):
        self.ROOT = kwargs["ROOT"]
        self.websocket_config = kwargs["websocket_config"]
        self.path = self.websocket_config.pop("path", "")
        self.protocol = self.websocket_config.pop("protocol", "ws")
        self.salt = self.websocket_config.pop("salt", "")
        self.system_uid = self.websocket_config.pop("system_uid", "system")
        self.workers_dir = self.websocket_config.pop("workers_dir", ["works/websocket"])
        self.workers = WebSocketRoute.get_workers(self.ROOT, self.workers_dir)
        self.conns = {}

    async def handler(self, websocket):
        if not self.auth(websocket):
            raise Exception("没经授权的请求：%s(%s:%s)" % (self.client_key(websocket), *websocket.remote_address[:2]))

        logging.warning("新链接:%s(%s:%s)" % (self.client_key(websocket), *websocket.remote_address[:2]))

        while True:
            try:
                message = await websocket.recv()

                # 更优的方式实现批量发送
                if message:
                    try:
                        message = json.loads(message)
                    except Exception as e:
                        logging.error(format_exc())
                        logging.error("message require JSON format")
                        await websocket.send("Error:message require JSON format")
                    event = message.get("__event__", "")
                    if not event:
                        logging.error("event can not empty value")
                        await websocket.send("Error:event can not empty value")
                    if event not in self.workers:
                        logging.error("event name %s not found!" % event)
                        await websocket.send("Error:event name %s not found!" % event)
                    else:
                        self.current_event = event
                        # websockets.broadcast(self.conns, json.dumps(message))
                        # await websocket.send(json.dumps(message))
                        self.current_conn = websocket

                        func = self.workers[event]
                        func.socket = self
                        define = inspect.getfullargspec(func)
                        if define.args:
                            self.workers[event](self, **message)
                        else:
                            self.workers[event](**message)
            except Exception as e:
                # ping的时间段内，没有收到客户端回应，将自动断开客户端连接
                if isinstance(e, (websockets.ConnectionClosedOK,
                                  websockets.ConnectionClosedError,
                                  websockets.ConnectionClosed)):
                    if self.client_key(websocket) in self.conns:
                        self.remove_client(websocket)

                    logging.warning("连接已断开：%s(%s:%s)" % (self.client_key(websocket), *websocket.remote_address[:2]))
                    # websocket.close_connection()    # 关闭当前线程连接
                    # websocket.close()               # 当连接断开，或者ping不他不通时(ping_interval)，主动关闭当前线程连接
                    break
                else:
                    logging.error(format_exc())
                    logging.error(str(e))

    async def main(self):
        # 每一个连接都单独一个线程
        async with websockets.serve(self.handler,
                                    **self.inspect_args()
                                    # "localhost", 8765,
                                    # ping_interval=20,
                                    # 一旦连接打开，每秒钟发送一个Ping帧ping_interval 。这用作保活。它有助于保持连接打开，尤其是在非活动连接上存在短暂超时的代理的情况下。设置ping_interval为None禁用此行为。
                                    # create_protocol=websockets.basic_auth_protocol_factory(
                                    #     realm="my dev server",
                                    #     credentials=("hello", "iloveyou"),
                                    # )
                                    ):
            await asyncio.Future()  # run forever


    def start(self):
        asyncio.run(self.main())

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    kwargs = {
        "ROOT": '/Users/lcylln/www/lcyframepy3/lcyframe3-demo',
        "websocket_config": {
            "host": "127.0.0.1",
            "port": 8765,
            "workers_dir": "/Users/lcylln/www/lcyframepy3/lcyframe3-demo/works/socket"
        }}
    wk = WebSocketWorker(**kwargs)
    wk.start()
