#!/usr/bin/env python
import sys
import asyncio
import websockets
import inspect

from base import BaseModel
from lcyframe import yaml2py
from lcyframe import ServicesFindet
from lcyframe.websocket_server import WebSocketWorker
from context import InitContext

# args = [item.split("=")[-1] for item in sys.argv if item.startswith("--config")]
sys.argv = sys.argv[:1]
config = InitContext.get_context()

conns = set()

# async def handler(websocket):
#     conns.add(websocket)
#     ws = None
#     try:
#         async for message in websocket:
#             # await websocket.send(message)
#
#             # 全体发送
#             for ws in conns:
#                 if ws:
#                     try:
#                         await ws.send(message)
#                     except websockets.ConnectionClosedOK as e:
#                         print("连接已断开：%s:%s" % ws.remote_address[:2])
#                         if ws in conns:
#                             conns.remove(ws)
#     except Exception as e:
#         if ws in conns:
#             conns.remove(ws)
#         print(str(e))   # websockets.ConnectionClosedOK


async def handler(websocket):
    conns.add(websocket)

    while True:
        try:
            message = await websocket.recv()

            # 循环发送速度过快，容易造成网络阻塞，导致资源暂满网络缓冲区，可以用背压，没100毫秒发送一批数据
            # for ws in conns:
            #     await ws.send(message)

            # 更优的方式实现批量发送
            if message:
                websockets.broadcast(conns, message)
        except Exception as e:
            if websocket in conns:
                conns.remove(websocket)
                print("连接已断开：%s:%s" % websocket.remote_address[:2])
            else:
                # websocket.close_connection()    # 关闭当前线程连接
                websocket.close()                 # 当连接断开，或者ping不他不通时(ping_interval)，主动关闭当前线程连接
            break

async def main():
    # 每一个连接都单独一个线程
    async with websockets.serve(handler, "localhost", 8765,
                                ping_interval=20,   # 一旦连接打开，每秒钟发送一个Ping帧ping_interval 。这用作保活。它有助于保持连接打开，尤其是在非活动连接上存在短暂超时的代理的情况下。设置ping_interval为None禁用此行为。
                                # create_protocol=websockets.basic_auth_protocol_factory(
                                #     realm="my dev server",
                                #     credentials=("hello", "iloveyou"),
                                # )
                                ):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    # asyncio.run(main())

    websocket = WebSocketWorker(**config)
    yaml2py.impmodule(BaseModel, "model")  # 换为载入model父类，切worker的函数继承了model父类，所以可以使用所有的model子类
    ServicesFindet(websocket, BaseModel)(config)  # 获取全站所有连接库，赋值给BaseModel，继承了BaseModel的worker内，含有mqtt生产者连接，可以使用生产者创建新的任务
    websocket.model = BaseModel.model
    websocket.start()