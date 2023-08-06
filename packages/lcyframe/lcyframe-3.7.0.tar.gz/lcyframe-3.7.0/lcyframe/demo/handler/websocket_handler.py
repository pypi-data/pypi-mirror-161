#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import route
from lcyframe import funts
from base import BaseHandler
from tornado.websocket import WebSocketHandler

"""
WebSocket协议
已handler的模式启动WebSocket服务，实现模拟聊天室功能
https://www.tornadoweb.org/en/branch5.1/_modules/tornado/websocket.html
"""

@route("/websocket")
class WebSocketHandlerHandler(WebSocketHandler, BaseHandler):
    """
    websocket协议
    仅接受前端ws连接，如app采用多进程部署，每个进程都会有一个websocket服务，且相互隔离；所以不同的请求，可能返回不同的socket连接
    连接地址：url = ws://localhost:8000/wechat?nickname=张三
    .. js连接代码：
    var ws = new WebSocket(url);
      ws.onopen = function() {
         ws.send("Hello, world");
      };
      ws.onmessage = function (evt) {
         alert(evt.data);
      };

    .. python 连接：
    from tornado.websocket import websocket_connect
    from tornado.gen import engine
    from tornado.ioloop import IOLoop
    class WebSocketConn(object):
        @engine
        def connection(self):
            conn = yield websocket_connect("ws://192.168.2.50:6677/wechat?nickname=四张K")
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

    .. 在线测试：http://coolaf.com/tool/chattest
    """

    users = set()                   # 用来存放在线用户的容器
    def open(self):
        print('收到新的WebSocket连接')
        self.users.add(self)        # 建立连接后添加用户到容器中
        nickname = self.get_argument("nickname")
        for u in self.users:        # 向已在线用户发送消息
            u.write_message(u"[%s(%s)] 进入聊天室" % (nickname, self.request.remote_ip))

    def on_message(self, message):
        nickname = self.get_argument("nickname")
        # message = json.loads(message)
        print(type(message),message)
        for u in self.users:        # 向在线用户广播消息
            if u == self:continue
            u.write_message(u"[%s(%s)] 说：%s<br> &nbsp&nbsp&nbsp&nbsp" % (nickname, self.request.remote_ip, message))

    def on_close(self):
        nickname = self.get_argument("nickname")
        print(u"[%s(%s)] 离开聊天室" % (nickname, self.request.remote_ip))
        self.users.remove(self)     # 用户关闭连接后从容器中移除用户

        # 通知其他在线用户
        for u in self.users:
            u.write_message(u"[%s] 离开聊天室" % (nickname))

    def check_origin(self, origin):
        # 允许WebSocket的跨域请求
        return True
            
        

