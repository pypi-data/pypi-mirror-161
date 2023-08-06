#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from lcyframe import route
from lcyframe import funts
from base import BaseHandler, helper
import re

@route("/upload")
class UploadHeadHandler(BaseHandler):
    """
    上传
    """

    @helper.admin()
    def post(self):
        """

        :return:
        :rtype:
        """
        filedata = self.params.pop("file")
        info = self.helper.get_fileinfo(filedata)
        if info["format"] not in ["xlsx", "slx"]:
            raise self.api_error.FileFormatError
        if info["size"] >= 1024 * 1024 * 1:
            raise self.api_error.UploadError("大小不能超过1M")

        filename, savepath = self.helper.save_filedata(filedata,
                                                       os.path.join(self.app_config["ROOT"],
                                                                    self.app_config["data_config"]["base"],
                                                                    "project")
                                                       )

        self.write_success({"file_metadata": info})