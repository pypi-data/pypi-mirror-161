#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lcyframe import route
from lcyframe import funts
from base import BaseHandler

@route("/demo")
class DemoHandler(BaseHandler):
    """
    演示
    """

    @funts.params()
    def post(self):
        """添加
        测试post
        
        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - c # 手机号 type: string
        - d # 城市全拼列表 type: int
        - pic # 文件 type: file
        

        :return:
        :rtype:
        """
        # 上传文件 self.request.files = {'excel': [{'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}]
        excel = self.params["excel"]  # {'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}

        self.write_success()
        

    @funts.params()
    def get(self):
        """查看
        测试get

        Request extra query params:
        - a # 角色id type: integer
        - b # 供应商id type: string
        - d # 城市全拼列表 type: int


        :return:
        :rtype:
        """
        # 发送邮件
        self.smtp.send_email(
            ["452809783@qq.com", "123220663@qq.com"],
            "邮件标题6",
            message="文本",
            html_message="""
                <p style="color:red">邮件文本内容</p>
                <p><a href="http://www.xxx.com">链接</a></p>
                <p>内容中的图片未被显示时，需添加发件人信任。或者点击邮件页面中的"显示图片 信任此发件人的图片"</p>
                <p><img src="https://www.runoob.com/wp-content/uploads/2016/04/smtp4.jpg"></p>
                <p>图片标签：以下需添加image1的标签图片</p>
                <p><img src="cid:image1"></p>
                <p>2222</p>
                """,
            images=["/Users/apple/Downloads/WX20220714-160954@2x.png"],
            attachs=["/Users/apple/Downloads/WX20220714-154222@2x.png"]
        )
        # redis
        # self.redis.set("a", 1)
        # self.redis.get("a")

        # ssdb
        # self.ssdb.set("a", 1)
        # self.ssdb.get("a")

        # mq调用方法
        # self.mq.put({"event": "event1", "a": 1})

        # nsq调用方法
        # self.nsq.pub("test", '{"event": "on_create_user", "uid": 0}')
        # from producer.nsq import user
        # user.PublishUser().on_create_user({"uid": 0})
        # self.nsq.NsqEvent.on_create_user({"uid": 0})

        # mqtt调用方法,2种方法不可同时使用，否则会抢占链接
        # from producer.mqtt import user
        # user.MqttEvent().on_create_user({"a": "mqtt_test"})
        # self.mqtt.MqttEvent.on_create_user({"a": "mqtt_test"})

        # celery
        # self.celery.Events.save_image.delay(111)
        # self.celery.Events.UserEvent.register.delay(111)

        # beanstalk
        # self.beanstalk.ClassName.func({"DemoEvents": 1}, priority=65536, delay=0, ttr=60, tube="tube_name")
        # self.beanstalk.DefaultEvents.event({"DefaultEvents": 1})  # tube1
        # self.beanstalk.DemoEvents.event({"DemoEvents": 1})        # tube2

        # 上传文件 self.request.files = {'excel': [{'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}]
        # excel = self.params["excel"]    # {'filename': 'xxxxxxx.xlsx', 'body':"xxxxxx"}

        # graylog
        # self.graylog.from_server(x="sdsdds")
        # 调用model，创建一条用户数据

        self.model.DemoModel.get_demo(1)
        self.websocket.Events.demo(**{"a": 1, "b": 2})
        self.write_success()






