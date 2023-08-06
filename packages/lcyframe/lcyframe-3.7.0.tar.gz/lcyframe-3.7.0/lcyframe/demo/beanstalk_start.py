# coding=utf-8
import sys
from base import BaseModel
from lcyframe import yaml2py
from lcyframe import ServicesFindet
from lcyframe.beanstalk_server import BeanstalkWorker
from context import InitContext

# 监听的tube的优先级：命令行参数>配置文件指定>消费者指定的所有tube（默认）
# python beanstalk_start.py --watch=tube1,tube2,tube3
watch = sys.argv[1].replace(" ", "").strip("--watch=").strip("-W").lstrip("=").split(",") if len(sys.argv) > 1 else []
sys.argv = sys.argv[:1]
config = InitContext.get_context()
if watch:
    config["beanstalk_config"]["watch"] = watch

tasks = BeanstalkWorker(**config)
yaml2py.impmodule(BaseModel, model_dir="model")
ServicesFindet(tasks, BaseModel)(config)
tasks.start()
