#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from test_script import *
from lcyframe.libs import cprint



def demo():
    headers = {"uid": 100000}

    params = {
        "a": 1
    }

    return admin_login_and_send(
        methed="get",
        url="/demo",
        params=params,
        headers=headers,
    )


if __name__ == "__main__":
    demo()

