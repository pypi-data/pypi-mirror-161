# -*- coding:utf-8 -*-
from lcyframe.libs.errors import ApiError as BaseError
from lcyframe.libs.errors import *
from falcon.status_codes import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN


class ApiError(BaseError):
    code = 1
    code_name = 'Api Runtime Error'
    message = 'Runtime api error occurred.'
    status = HTTP_BAD_REQUEST

    def __init__(self, message=None, code=None, code_name=None, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)
        # if zh_message:
        #     self.zh_message = zh_message
        if message:
            self.message = message
        else:
            if hasattr(self, "zh_message") and self.zh_message:
                self.message = self.zh_message
        if code is not None:
            self.code = code
        if code_name is not None:
            self.code_name = code_name

    def to_dict(self, *args, **kwargs):
        return {
            'err_code': self.code,
            'err_name': self.code_name,
            'message': self.message
        }


class DemoObjectError(ApiError):
    """
    自定义错误对象
    """
    code = 1000
    code_name = 'DemoObjectError'
    message = 'DemoObjectError'
    zh_message = '自定义错误说明'

class ErrorSystemAPI(ApiError):
    """
    ******
    """
    code = 2000
    code_name = 'Api server is prohibition'
    zh_message = 'API服务暂停访问！'
    help = "系统升级中..."

