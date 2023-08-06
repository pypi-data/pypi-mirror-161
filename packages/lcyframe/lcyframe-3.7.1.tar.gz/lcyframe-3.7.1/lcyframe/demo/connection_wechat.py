from tornado.websocket import websocket_connect
from tornado.gen import engine
from tornado.ioloop import IOLoop

"""
基于ioloop连接到已handler的形式启动的tornado.websocket服务
url：ws://192.168.2.50:6677/wechat
类型http的模式提交ws消息

区别：https://www.jianshu.com/p/59b5594ffbb0/
socket:TCP/IP协议的封装，适用服务端与其他服务端
websocket:是html5规范中的一个部分,它借鉴了socket这种思想提供web应用程序和服务端全双工通信应用层协议.适用app、web应用
"""

class WebSocketConn(object):
    @engine
    def connection(self):
        conn = yield websocket_connect("ws://0.0.0.0:12345")
        while True:
            # msg = yield conn.read_message()
            # if msg is None: break
            # print("收到信息：%s" % msg)

            conn.write_message("回复消息：%s" % "回复消息，时代大厦")


if __name__ == "__main__":
    ioloop = IOLoop.instance()
    ws = WebSocketConn()
    ioloop.add_callback(ws.connection)
    ioloop.start()