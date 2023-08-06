#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from lcyframe.libs.singleton import MongoCon
from model.business_model import BusinessSchema
from model.user_model import UserSchema
from context import InitContext
config = InitContext.get_context()

def init_db():
    db = MongoCon().get_database(**config["mongo_config"])
    if not db.business.count():
        # 初始化商户
        business = vars(BusinessSchema())
        business["name"] = "anhua"
        db.business.insert(business)

        # 新增第一个用户
        from lcyframe.libs.aes import AES
        user = vars(UserSchema())
        user["uid"] = 1
        user["username"] = "anhua"
        user["nickname"] = "安华"
        user["password"] = AES(key=config["aes_config"]["secret"]).encode("000000")
        user["business_id"] = str(business["_id"])
        db.user.insert(user)

def mkdir():
    os.system("mkdir -p ./data/images/head")
    os.system("mkdir -p ./data/bak")
    os.system("mkdir -p ./data/case")
    os.system("mkdir -p ./data/files")
    os.system("mkdir -p ./data/tmp")

if __name__ == "__main__":
    init_db()
    mkdir()