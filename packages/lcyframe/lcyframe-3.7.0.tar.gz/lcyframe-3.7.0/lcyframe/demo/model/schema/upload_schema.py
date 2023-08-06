#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bson.objectid import ObjectId
from base import BaseSchema
import time


class UploadSchema(BaseSchema):
    """
    上传文件
    """

    collection = "upload"

    def __init__(self):
        self._id = ObjectId()

