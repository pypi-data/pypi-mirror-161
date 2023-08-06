#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.websocket_schema import WebSocketSchema

class WebsocketModel(BaseModel, WebSocketSchema):

    @classmethod
    def _parse_data(cls, doc, **kwargs):
        """
        组装、修正单条记录
        该方法若存在，框架会自动使用
        若不存在，则模式使用框架内置方法
        :param doc: 单条数据
        :param kwargs:
        :return:
        """
        if not doc:
            return {}

        if "_id" in doc:
            doc["websocket_id"] = doc.pop("_id", "")

        return doc

    @classmethod
    def get_websocket(cls, websocket_id, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        return cls.find_one_by_oid(websocket_id)


    @classmethod
    def get_websocket_by_spec(cls, spec, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        return cls.find_one(spec)


    @classmethod
    def get_websocket_list_by_last_id(cls, last_id, count, **kwargs):
        """
        前端列表
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, last_id = cls.find_list_by_last_id(spec,
                                                      count,
                                                      sort=[("create_at", -1), ],
                                                      fields=kwargs.get("fields", None),
                                                      last_id_field=False)
        return data_list, last_id

    @classmethod
    def get_websocket_list_by_page(cls, page, count, **kwargs):
        """
        后台列表
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, pages, counts = cls.find_list_by_page(spec,
                                                         page,
                                                         count,
                                                         sort=[("create_at", -1), ],
                                                         fields=kwargs.get("fields", None))
        return data_list, pages, counts

    @classmethod
    def create_websocket(cls, *args, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        pass

    @classmethod
    def modify_websocket(cls, *args, **kwargs):
        """
        修改
        :return:
        :rtype:
        """
        pass

    @classmethod
    def delete_websocket(cls, websocket_id, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        return cls.update({"_id": websocket_id}, {"state": -1})




