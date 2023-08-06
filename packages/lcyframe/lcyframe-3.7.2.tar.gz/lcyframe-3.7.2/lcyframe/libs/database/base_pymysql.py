import datetime
import logging
try:
    import pymysql
    from dbutils.pooled_db import PooledDB
    from dbutils.persistent_db import PersistentDB
except:
    print("not found model pymysql")


class PyMysqlPooledDB(object):
    """
    链接池
    用于一般应用服务
    """
    __pool = None

    def __init__(self, **kwargs):
        """

        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量0，禁止共享链接，确保线程安全
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param password:密码
        :param charset:字符编码
        """

        if not self.__pool:
            cursorclass = {1: pymysql.cursors.DictCursor,
                           2: pymysql.cursors.Cursor}[kwargs.get("cursorclass", 1)]
            self.__class__.__pool = PooledDB(pymysql,       # 默认pymysql.threadsafety=1，确保线程安全。线程可以共享模块，但不能共享连接。
                                             host=kwargs.get("host", "127.0.0.1"),
                                             port=kwargs.get("port", 3306),
                                             user=kwargs.get("user", 'root'),
                                             password=str(kwargs.get("password", "")),
                                             database=kwargs.get("database", "test"),
                                             mincached=kwargs.get("mincached", 10),
                                             maxcached=kwargs.get("maxcached", 20),
                                             maxconnections=kwargs.get("maxconnections", 512),
                                             maxusage=kwargs.get("maxusage", 100),
                                             blocking=kwargs.get("blocking", False),
                                             setsession=kwargs.get("setsession", None),
                                             reset=kwargs.get("reset", True),
                                             charset=kwargs.get("charset", "utf8mb4"),
                                             cursorclass=cursorclass
                                             )

        self.conn = self.__pool.connection(shareable=True)  # shareable=True, 所有线程共享链接.False线程专用，每次调用回分配一个空闲链接，可能不一样
        self.cursor = self.conn.cursor()
        self.autocommit_mode = kwargs.get("autocommit", True)  # True 每次执行自动提交事务；False 需手动调用commit()提交事务

    def select_one(self, sql, params=None):
        """
        :param sql: qsl语句
        :param param: sql参数
        :example:
            select_one("select * from demo where name=%s", params=(2, ))
        """
        self.__execute(sql, params)
        result = self.cursor.fetchone()
        """:type result:dict"""
        result = self.__dict_datetime_obj_to_str(result)
        return result

    def select_all(self, sql, params=None):
        """
        :param sql: qsl语句
        :param param: sql参数
        :return: 结果数量和查询结果集
        :example:
            self.select_all('select * from demo where name=%s', (2,))
        """
        count = self.__execute(sql, params)
        result = self.cursor.fetchall()
        """:type result:list"""
        [self.__dict_datetime_obj_to_str(row_dict) for row_dict in result]
        return result

    def insert(self, table, insert_data, many=False, new=True):
        """
        from pymysql.converters import escape_string
        content: escape_string(content)
        :param table:
        :param insert_data  type:[{"field1": 1},{"field2": 2}]
        :param many  type: true 批量写入（last_insert_id()得到的值不准确）
                           false 逐条写入（last_insert_id()得到的值为准确值,需要获得最新的id值，请使用逐条写入）
                           last_insert_id(): 当前连接，整个数据库内，上一次insert事务提交后，生成的最后一个自增key的值,
                           若连接断开，则值为0
        :param new  type: 若id为自增键时，True 返回最新记录，False返回影响条数
        :return:count 1 影响的行数
        """
        count = 0
        last_insert_ids = []
        insert_datas = insert_data if isinstance(insert_data, (list, tuple)) else [insert_data]
        try:
            columns = ','.join(list(insert_datas[0].keys()))
            params = [tuple(data.values()) for data in insert_datas]
            values = (len(params[0]) * "%s,").rstrip(",")
            sql = "insert into " + table + " (" + columns + ") values (" + values + ")"
            if many:
                count = self.cursor.executemany(sql, params)
            else:
                for item in params:
                    count += self.cursor.execute(sql, item)
                    if new:
                        self.cursor.execute("select last_insert_id() as id")
                        result = self.cursor.fetchone()
                        if result:
                            last_insert_ids.append(result["id"])
            self.__commit()
        except Exception as e:
            self.rollback()
            raise e
        else:
            if new:
                if not isinstance(insert_data, (list, tuple)):
                    sql = f'select * from {table} where id = %s'
                    return self.select_one(sql, last_insert_ids[0])
                else:
                    sql = f'select * from {table} where id in %s'
                    return self.select_all(sql, [tuple(last_insert_ids)])
            else:
                return count

    def inserts(self, table, insert_data, new=False):
        """
        批量写入
        new： True 返回新写入的数据列表（写入为逐条写入，非原子性） False不返回最新数据，只返回影调条数（原子写入）
        """
        if new:
            datas = self.insert(table, insert_data, many=False, new=True)
            return datas
        else:
            counts = self.insert(table, insert_data, many=True, new=False)
            return counts

    def update(self, sql, params=None):
        """
        :param sql:
        :param params:
        :return:
        :example:
            # update all data
            self.update('update demo set name=22 where name=%s', (2,))
            # update first one with order asc
            self.update('update demo set name=2 where name=%s order by id limit 1', (22,))
        """
        count = self.__execute(sql, params)
        return count

    def delete(self, sql, params=None):
        """
        :param sql:
        :param params:
        :return:
        :example:
            # delete all data
            self.delete('delete from demo where name=%s', (22,))
            # delete first one with order asc
            self.delete('delete from demo where name=%s order by id limit 1', (22,))
        """
        count = self.__execute(sql, params)
        return count

    def query_sql(self, sql, params=None):
        """
        查询数据
        sql不要拼接或采用format()，请用传参方式，防止注入

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.

        :param sql:
        :param param:
        :example::
            data = query_sql("select * from demo where name=%s and id=%s", (1, 2))
            data = query_sql("select * from demo where name=%(name)s", {"name": 2})
            data = query_sql("select * from demo where name=name", {"name": 2})
        :return:

        """
        try:
            self.execute(sql, params)
        except Exception as e:
            logging.error(sql)
            raise e
        else:
            result = self.cursor.fetchall()
            return result or []

    def execute(self, sql, params=None):
        """
        提交数据
        原生执行，sql不要拼接.format，用传参方式，防止注入
        常用于：insert、delete、update
        :param sql:
        :param param: [1, 2]、[(1, 2), (3, 4)]
        :return:
        """
        count = 0
        try:
            count = self.__execute(sql, params)
        except Exception as e:
            logging.error(sql)
            self.rollback()
            raise e
        else:
            return count

    def begin(self):
        """开启事务: 先关闭自动提交模式"""
        self.conn.begin()

    def end(self, option='commit'):
        """
        结束事务：
        提交事务或回滚
        还原事务提交模式
        """
        if option == 'commit':
            self.commit()
        else:
            self.rollback()

    def commit(self):
        """手动提交事务"""
        self.conn.commit()

    def rollback(self):
        """
        回滚
        :return:
        """
        self.conn.rollback()

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            raise e

    def parse_set_condition_value(self, **params):
        sql_columns = ""
        for k in params.keys():
            sql_columns += k + "=%s,"
        sql_columns = sql_columns.rstrip(",")
        sql_values = params.values()
        return sql_columns, list(sql_values)

    def __commit(self):
        """按当前autocommit配置，决定是否提交事务"""
        if self.autocommit_mode:
            return self.conn.commit()
        else:
            pass    # 需手动调用self.commit()提交

    def __execute(self, sql, params=None):
        count = self.cursor.execute(sql, params)
        self.__commit()
        return count

    @staticmethod
    def __dict_datetime_obj_to_str(result_dict):
        """把字典里面的datatime对象转成字符串"""
        if result_dict:
            result_replace = {k: v.__str__() for k, v in result_dict.items() if isinstance(v, datetime.datetime)}
            result_dict.update(result_replace)
        return result_dict


class PyMysqlPersistentDB(PyMysqlPooledDB):
    """
    用于多线程编程
    线程专用链接模式
    """
    __pool = None

    def __init__(self, **kwargs):
        if not self.__pool:
            cursorclass = {1: pymysql.cursors.DictCursor,
                           2: pymysql.cursors.Cursor}[kwargs.get("cursorclass", 1)]
            self.__class__.__pool = PersistentDB(
                host=kwargs.get("host", "127.0.0.1"),
                port=kwargs.get("port", 3306),
                user=kwargs.get("user",'root'),
                password=str(kwargs.get("password", "")),
                database=kwargs.get("database", "test"),
                creator=pymysql,                                # 使用链接数据库的模块# 默认pymysql.threadsafety=1，确保线程安全。线程可以共享模块，但不能共享连接。
                maxusage=kwargs.get("maxusage", None),          # 一个链接最多被重复使用的次数，None表示无限制
                setsession=kwargs.get("setsession", []),        # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                closeable=kwargs.get("closeable", False),       # 如果为False时， conn.close() 实际上被忽略，供下次使用，主线程关闭时才会关闭链接。如果为True时， conn.close()则关闭链接，那么再次调用pool.connection时就会报错。（pool.steady_connection()可以获取一个新的链接）
                threadlocal=kwargs.get("threadlocal", None),    # 本线程独享值得对象，用于保存链接对象，如果链接对象被重置
                charset=kwargs.get("charset", "utf8mb4"),
                cursorclass=cursorclass
            )
        self.conn = self.__pool.connection(shareable=False)    # False不共享链接。 同一个主进程线程/子线程独占链接。不同的线程/子线程间，链接不一样
        self.cursor = self.conn.cursor()
        self.autocommit_mode = kwargs.get("autocommit", True)  # True 每次执行自动提交事务；False 需手动调用commit()提交事务


