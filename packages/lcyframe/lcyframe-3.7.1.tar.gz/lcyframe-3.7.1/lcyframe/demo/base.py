#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import BaseHandler as Handler
from lcyframe import BaseModel as Model
from lcyframe import BaseSchema as Schema
from utils import errors, helper, keys
from lcyframe import utils

class BaseHandler(Handler):
    """
    This is the base class RequestHandler you apply
    You can rewrite the function you want and inherit the frame parent class
    """
    api_error = errors
    helper = helper
    keys = keys

    def write(self, chunk):
        if type(chunk) is dict and chunk.get("code") == 0:
            chunk['code'] = 200
        return super(BaseHandler, self).write(chunk)

    def write_pagination(self, datas, counts, **kwargs):
        """
        返回列表
        :param counts: 总条数
        :param datas:
        :return:
        """
        data = {"datas": datas,
                "pagination": {"counts": counts,
                               "page": self.params.get("page", 1),
                               "count": self.params.get("count", 10),
                               }}
        if "pages" in kwargs:
            data["pagination"]["counts"] = kwargs.pop("pages", 0)

        else:
            pages = counts / self.params.get("count", 10)
            remainder = counts % self.params.get("count", 10)
            if remainder:
                pages += 1

            data["pagination"]["pages"] = pages

        data.update(kwargs)
        self.write_success(data)

class BaseModel(Model):
    """
    This is the base class Model you apply
    You can rewrite the function you want and inherit the frame parent class
    """
    api_error = errors
    helper = helper
    keys = keys


class BaseSchema(Schema):

    @classmethod
    def shard_rule(cls, shard_key_value):
        """
        :param shard_key_value:
        :return: table_value

        This is default rule by `mod10`
        you can rewrite like this

        :example :: DemoSchema.yml
            def shard_rule(shard_key_value):
                do_your_thing
                ...
        """
        return cls.mod10(shard_key_value)

    @classmethod
    def __parse_oid(cls, d):
        for k in ["create_at", "update_at", "start_at", "end_at"]:
            prefix, _ = k.split("_")
            if k in d:
                if isinstance(d[k], str) and d[k].isdigit():
                    d[k] = int(d[k])
                d["%s_date" % prefix] = utils.timestamp2str(d[k], "%Y-%m-%d %H:%M:%S")
        return Schema.__parse_oid(d)

    @classmethod
    def create_data(cls, *args, **kwargs):
        docs = cls.fields()
        for k, v in kwargs.items():
            if k not in docs:
                continue
            docs[k] = v

        data = BaseModel.mysql.insert(cls.collection, docs)
        if hasattr(cls, "_parse_data"):
            return cls._parse_data(data)
        else:
            return data

    @classmethod
    def update_data(cls, id, **kwargs):
        kwargs["update_time"] = utils.datetime.now()
        sql_condition, sql_params = cls.get_value_symbol(kwargs, "set")
        sql = f"update {cls.collection} set {sql_condition} where id={id}"
        return BaseModel.mysql.update(sql, sql_params)

    @classmethod
    def get_data_by_spec(cls, *args, **kwargs):
        """
        单条记录
        :return:
        :rtype:
        """
        values = ",".join(args) or "*"
        sql_cond, sql_params = cls.get_value_symbol(kwargs)
        sql = f"select {values} from {cls.collection} where {sql_cond}"
        data = BaseModel.mysql.select_one(sql, sql_params)
        if hasattr(cls, "_parse_data"):
            return cls._parse_data(data)
        else:
            return data

    @classmethod
    def get_batch_by_spec(cls, *args, **kwargs):
        """
        多条记录
        :return:
        :rtype:
        """
        values = ",".join(args) or "*"
        sql_cond, sql_params = cls.get_value_symbol(kwargs)
        sql = f"select {values} from {cls.collection} where {sql_cond}"
        datas = BaseModel.mysql.select_all(sql, sql_params)
        return [cls._parse_data(data) for data in datas] if datas else []

    @classmethod
    def get_value_symbol(cls, condition_data, sql_type="and"):
        def __symbol_str(condition, symbol_str, sql_params):
            if isinstance(condition, (list, tuple)):
                if len(condition) == 1:
                    symbol = " = "
                    value = condition
                else:
                    symbol = f" {condition[0]} "
                    value = condition[1]
            else:
                symbol = " = "
                value = condition

            if "between" in symbol.lower():
                symbol_str.append(f"{k}{symbol}%s and %s")
                sql_params.append(value[0])
                sql_params.append(value[1])
            elif "in" in symbol.lower():
                symbol_str.append(f"{k}{symbol}%s")
                sql_params.append(tuple(value))
            else:
                symbol_str.append(f"{k}{symbol}%s")
                sql_params.append(value)

            return symbol_str, sql_params

        condition_data = condition_data if isinstance(condition_data, (list, tuple)) else condition_data.items()
        symbol_str = []
        sql_params = []
        for k, items in condition_data:
            if isinstance(items, (dict,)):
                for item in items.items():
                    symbol_str, sql_params = __symbol_str(item, symbol_str, sql_params)
            elif isinstance(items, (list, tuple)):
                if isinstance(items[0], (str, bytes)):
                    symbol_str, sql_params = __symbol_str(items, symbol_str, sql_params)
                else:
                    for item in items:
                        symbol_str, sql_params = __symbol_str(item, symbol_str, sql_params)
            else:
                symbol_str, sql_params = __symbol_str(items, symbol_str, sql_params)

        if sql_type == "set":
            sql_condition = f",".join(symbol_str) if symbol_str else ""
        else:
            sql_condition = f" {sql_type} ".join(symbol_str) if symbol_str else ""
        # return sql_condition, sql_params if len(sql_params) > 1 else sql_params[0] if len(sql_params) == 1 else sql_params
        return sql_condition, sql_params

    @classmethod
    def _get_list_by_page(cls, page, count, **kwargs):
        """
        分页
        调用例子：
            page: 1
            count:10
            kwargs:
                ... sql='select * from user where  company_id=%s and id=%s', params=[1, 33]

                ... sql_and={'company_id': 1, 'id': 33}
                ... sql_and={'company_id': 1, 'id': [">=", 33]}, orderby={'id': 1, create_at: -1}
                ... sql_and={'company_id': 1, 'id': ["in", (33, 34)]}, orderby={'id': 1, create_at: -1}
                ... sql_and={'company_id': 1, 'create_time': {"between": [start_time, end_time]}}
                ... sql_and={'company_id': 1, 'create_time': ["between", (start_time, end_time)]}
                ... sql_and={'company_id': 1, 'create_time': {">": start_time, "<=": end_time}}
                ... sql_and={'company_id': 1, 'create_time': [(">", start_time), ("<=", end_time)}

                ... sql_or={'company_id': 1, 'gid': ["in", (1, 2)]}
                ... sql_or={'account': {"REGEXP": self.params.get("search"),
                            'email': ["REGEXP", self.params.get("search")]
                        }

                ... orderby={'id': 1, create_at: -1}

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        values: 返回字段
            values = fields1,fields2,...
            values = [fields1,fields2,...]
        and条件：
            {"a":1, "b":2} 不关心查询顺序
            [("b", 2), ("a", 1)] 按顺序组装查询语句
        or条件: 推荐组装好sql在传入，例
            select * from user where a=1 and id=33 or id=28 ==> (a=1 and id=33) or id=28
            select * from user where a=1 and (id=33 or id=28) ==> (a=1 and id=33) or (a=1 and id=28)
        排序：orderby
            {"a":1, "b":-1} a升序，b将序，无序
            [("a", 1), ("b", -1)] a升序，b将序
        """

        params = kwargs.pop("params", [])
        values = kwargs.pop("values", "")
        sql = kwargs.pop("sql", "")
        if params and not sql:
            raise Exception("sql must be provided, if you given params")
        if not sql:
            if values:
                values = values if isinstance(values, str) else ",".join(values)
            else:
                values = "*"
            sql = f"select {values} from {cls.collection}"

        # and
        sql_and = kwargs.pop("sql_and", [])
        and_condition, and_symbol_params = cls.get_value_symbol(sql_and, "and")
        params.extend(and_symbol_params)

        # or
        sql_or = kwargs.pop("sql_or", [])
        or_condition, or_symbol_params = cls.get_value_symbol(sql_or, "or")
        or_condition = (" (" + or_condition + ") ") if or_condition else or_condition
        params.extend(or_symbol_params)

        # sql
        if and_condition or or_condition:
            if and_condition and or_condition:
                sql += " where " + " and ".join([and_condition, or_condition])
            elif and_condition:
                sql += " where " + and_condition
            else:
                sql += " where " + or_condition
        counts = cls.get_data_counts(sql, params)
        orderby = kwargs.pop("orderby", [])
        orderby = orderby if isinstance(orderby, (list, tuple)) else orderby.items()
        items = ["%s %s" % (k, "ASC" if v >= 1 else "DESC") for k, v in orderby]
        orderby_condition = ",".join(items) if items else ""
        if orderby_condition:
            sql += " order by " + orderby_condition
        limit = f" limit {(page - 1) * count}, {count}"
        sql += limit
        datas = BaseModel.mysql.query_sql(sql, params)

        return datas, counts

    @classmethod
    def get_data_counts(cls, sql, params=None):
        total_count = BaseModel.mysql.select_all(sql, params)
        counts = 0 if not total_count else len(total_count)
        return counts

    @classmethod
    def change_datetime(cls, docs, fields=None):
        """
        格式化时间
        """
        for i in fields or ["create_time", "update_time", "last_login"]:
            if i in docs and isinstance(docs[i], str) and "." in docs[i]:
                docs[i] = docs[i][:-7]
        return docs
