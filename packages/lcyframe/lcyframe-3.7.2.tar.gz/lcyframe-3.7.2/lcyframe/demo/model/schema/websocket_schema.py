#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from base import BaseSchema
import time


class WebSocketSchema(BaseSchema):
    """
    模拟聊天室
    """

    collection = "websocket"

    def __init__(self):
        self._id = ObjectId()

