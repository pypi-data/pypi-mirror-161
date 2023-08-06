#!/usr/bin/env python
# -*- coding:utf-8 -*-
from base import BaseModel
from model.schema.upload_schema import UploadSchema

class UploadModel(BaseModel, UploadSchema):

    @classmethod
    def get_upload(cls, upload_id, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        d = cls.find_one_by_oid(upload_id)
        return cls._parse_data(d)


    @classmethod
    def get_upload_by_spec(cls, spec, **kwargs):
        """
        详情
        :return:
        :rtype:
        """
        d = cls.find_one(spec)
        return cls._parse_data(d)


    @classmethod
    def get_upload_list_by_last_id(cls, last_id, count, **kwargs):
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
        return [cls._parse_data(d) for d in data_list if d], last_id

    @classmethod
    def get_upload_list_by_page(cls, page, count, **kwargs):
        """
        后台列表
        :return:
        :rtype:
        """
        spec = {}
        spec.update(kwargs.get("spec", {}))
        data_list, pages = cls.find_list_by_page(spec,
                                                 page,
                                                 count,
                                                 sort=[("create_at", -1), ],
                                                 fields=kwargs.get("fields", None))
        return [cls._parse_data(d) for d in data_list if d], pages

    @classmethod
    def create_upload(cls, *args, **kwargs):
        """
        创建
        :return:
        :rtype:
        """
        pass

    @classmethod
    def modify_upload(cls, *args, **kwargs):
        """
        修改
        :return:
        :rtype:
        """
        pass

    @classmethod
    def delete_upload(cls, upload_id, **kwargs):
        """
        删除
        :return:
        :rtype:
        """
        return cls.update({"_id": upload_id}, {"state": -1})

    @classmethod
    def _parse_data(cls, d, **kwargs):
        """
        组装单条数据
        :return:
        :rtype:
        """
        if not d:
            return {}

        d["upload_id"] = d.pop("_id", "")

        return d


