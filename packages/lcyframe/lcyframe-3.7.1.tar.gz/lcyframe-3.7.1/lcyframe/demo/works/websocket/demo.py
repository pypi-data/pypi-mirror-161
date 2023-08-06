# -*- coding: utf-8 -*-
import random, time
from lcyframe.libs.websocket_route import WebSocketRoute
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

"""
# 例子一：只接受消息
self.websocket.Event.demo1(**{"a": 1})
# 例子二：接受切需要向客户端发送消息，demo2定义时，需设置第一个位置参数，用法类似于celery的bind
self.websocket.Event.demo2(**{"a": 1})

http客户端发送websocket时的参数为：
{"__event__": "demo1/demo2", "a": 1, ...}
"""


@WebSocketRoute()
def demo1(**message):
    """
    不设置第一个位置参数，只用于接受消息
    """
    # do something
    pass

@WebSocketRoute()
def demo2(socket, **message):
    """
    设置第一个位置参数时，服务会把当前的socket对象绑定到第一个参数上
    socket: work对象，拥有与handler中的self一样的能力
    socket.current_conn: 当前的客户端连接
    message：收到的信息
    """
    # 推送给当前消息来源的的客户端；查询反馈场景
    # socket.send(**message)

    # 发送给指定客户端；定点发送场景
    # conn = socket.conns["uid:id"]   # 所有连接被收集，放置在conns内，key=uid:cliend_id
    # socket.send(conn,**message)

    # 推送消息给所有已连接的客户端（除系统和消息来源方)；聊天室场景
    socket.sendall(**message)
