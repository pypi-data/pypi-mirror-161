# coding=utf-8
import os
import time, json
import logging
import asyncio
from lcyframe.libs import utils


class WebSocketRoute(object):
    """消息队列路由"""
    _workers = {}

    def __init__(self, event=None):
        self.event = event

    def __call__(self, _handler):
        event = self.event and self.event or _handler.__name__
        _handler.from_route = True
        self._workers[event] = _handler
        return _handler

    @classmethod
    def tasks(cls, _handler):
        for event_name, event_obj in _handler.__dict__.items():
            if not event_obj:
                continue
            if type(event_obj) == str:
                continue
            if event_name in cls._workers:
                raise Exception("The event is exists multiple: `%s`" % event_name)
            cls._workers[event_name] = getattr(_handler, event_name)
        return cls._workers

    @classmethod
    def get_workers(cls, ROOT, workers_path):
        if not ROOT:
            raise Exception("the project dir path must been give， and None.")

        if not isinstance(workers_path, list):
            workers_path = [workers_path]

        if workers_path is None:
            raise Exception("args workers_path is not allow empty")

        if not cls._workers:
            for work in workers_path:
                for root, dirs, files in os.walk(utils.fix_path(os.path.join(ROOT, work))):
                    for file in files:
                        if file.startswith("__"):
                            continue
                        if file.endswith(".pyc"):
                            continue
                        if not file.endswith(".py"):
                            continue
                        model_name = root.replace(ROOT, "").lstrip("/").replace("/", ".") + "." + file.rstrip(".py")
                        __import__(model_name, globals(), locals(), [model_name], 0)
                        logging.debug("register socket workers [%s.py] success!" % model_name)
        return cls._workers



class Events(object):

    def __getattr__(self, event):
        if event not in self.__dict__:
            self.__dict__[event] = Agent(self.websocket, event)

        return self.__dict__[event]

class Agent:

    def __init__(self, websocket, event):
        self.websocket = websocket
        self.event = event

    def __repr__(self):
        return "event '%s'" % self.event

    def __call__(self, **body):
        payload = {}
        payload["__event__"] = self.event  # message_handler name by Consumer
        payload["ts"] = int(time.time())
        payload.update(body)
        return self.websocket.send(**payload)

