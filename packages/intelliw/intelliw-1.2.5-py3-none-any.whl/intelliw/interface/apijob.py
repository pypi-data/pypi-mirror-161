#!/usr/bin/env python
# coding: utf-8

import os
import json
import signal
import time
import datetime
import threading
import numpy as np
from intelliw.utils import message
from intelliw.config import config
from intelliw.core.infer import Infer
from intelliw.core.report import RestReport
from intelliw.core.linkserver import linkserver
from intelliw.utils.logger import get_logger
from intelliw.interface import apihandler
from intelliw.utils.util import JsonEncoder

from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder


class FlaskJSONEncoder(_JSONEncoder):
    """重载flask的json encoder, 确保jsonfy()能解析numpy的json"""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
            return obj.__str__()
        else:
            return super(FlaskJSONEncoder, self).default(obj)


class Flask(_Flask):
    """重载flask的jsonencoder, 确保能解析numpy的json"""
    json_encoder = FlaskJSONEncoder


logger = get_logger()


childs = []


def exit_handler(signum, frame):
    for child in childs:
        child.terminate()


class Application():
    """推理服务路由类
    example:
        @Application.route("/infer-api", method='get', need_featrue=True)
        def infer(self, test_data):
            pass
    args:
        path           访问路由   /infer-api
        method         访问方式，支持 get post push delete head patch options
        need_featrue   是否需要使用特征工程, 如果是自定义与推理无关的函数, 请设置False
    """

    # Set URL handlers
    HANDLERS = []
    HAS_INFER = False

    def __init__(self, custom_router):
        self.app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                         static_folder=os.path.join(os.path.dirname(__file__), "static"))
        self.__hander_process(custom_router)

    def __call__(self):
        return self.app

    @classmethod
    def route(cls, path, **options):
        def decorator(f):
            func = f.__name__
            if func == 'infer':
                cls.HAS_INFER = True
            cls.HANDLERS.append((path, apihandler.MainHandler, {'func': func, 'method': options.pop(
                'method', 'post'), 'need_featrue': options.pop('need_featrue', True)}))
            return f
        return decorator

    def __hander_process(self, router):
        # 加载自定义api, 配置在algorithm.yaml中
        for r in router:
            path, func, method, need_featrue = r["path"], r["func"], r.get(
                "method", "post").lower(), r.get("need_featrue", True)
            if func == 'infer':
                Application.HAS_INFER = True
            Application.HANDLERS.append((path, apihandler.MainHandler, {
                'func': func, 'method': method, 'need_featrue': need_featrue}))

        # 检查用户是否完全没有配置路由
        if len(Application.HANDLERS) == 0 or not Application.HAS_INFER:
            Application.HANDLERS.append((r'/predict', apihandler.MainHandler,
                                         {'func': 'infer', 'method': 'post', 'need_featrue': True}))  # 默认值

        # 集中绑定路由
        for r, _, info in Application.HANDLERS:
            f, m, nf = info.get('func'), info.pop(
                'method'), info.get('need_featrue')
            self.app.add_url_rule(r, view_func=apihandler.MainHandler.as_view(
                r), methods=[m], defaults=info)
            logger.info(f"方法: {f} 加载成功, 访问路径：{r}, 访问方法:{m}, 是否需要特征处理:{nf}")

        # healthcheck
        self.app.add_url_rule(
            '/healthcheck', view_func=apihandler.HealthCheckHandler.as_view("healthcheck"))


class ApiService:
    def __init__(self, port, path, response_addr):
        self.port = port        # 8888
        self.PERODIC_INTERVAL = config.PERODIC_INTERVAL if config.PERODIC_INTERVAL == 0 else 10
        self.reporter = RestReport(response_addr)

        infer = Infer(path, response_addr, self.PERODIC_INTERVAL)
        self.custom_router = infer.pipeline.custom_router
        self.app = Application(self.custom_router)()
        self.app.config.update({"infer": infer, "reporter": self.reporter})

        self._report_start()

    def _report_start(self):
        msg = [{'status': 'start', 'inferid': config.INFER_ID,
                'instanceid': config.INSTANCE_ID, 'inferTaskStatus': []}]
        self.reporter.report(
            message.CommonResponse(200, "inferstatus", '', json.dumps(msg, cls=JsonEncoder, ensure_ascii=False)))

    def _eureka_server(self):
        if config.START_EUREKA:
            linkserver.register(
                config.EUREKA_SERVER, config.EUREKA_PROVIDER_ID, config.EUREKA_APP_NAME, self.port)
            logger.info(
                f"eureka server register success, server name: {config.EUREKA_APP_NAME}")

    def _flask_server(self):
        from gevent.pywsgi import WSGIServer
        signal.signal(signal.SIGILL, exit_handler)
        if self.PERODIC_INTERVAL > 0:
            timer = threading.Timer(
                self.PERODIC_INTERVAL, self.perodic_callback)
            timer.daemon = True
            timer.start()
        WSGIServer(('0.0.0.0', self.port), self.app).serve_forever()

    def perodic_callback(self):
        infer = self.app.config["infer"]
        while True:
            infer.perodic_callback()
            time.sleep(self.PERODIC_INTERVAL)

    def run(self):
        self._eureka_server()
        self._flask_server()
