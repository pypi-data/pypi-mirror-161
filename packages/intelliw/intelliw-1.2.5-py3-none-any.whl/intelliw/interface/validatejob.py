#!/usr/bin/env python
# coding: utf-8

import os
import json
import signal
import traceback
from flask import Flask, views, jsonify, request
import intelliw.utils.message as message
from intelliw.config import config
from intelliw.utils.util import JsonEncoder
from intelliw.core.pipeline import Pipeline
from intelliw.utils.logger import get_logger

logger = get_logger()

childs = []
pipeline = None


def exit_handler(signum, frame):
    for child in childs:
        child.terminate()


class MainHandler(views.MethodView):
    def post(self):
        try:
            global pipeline
            r = request.json
            cfgs = r['transforms']
            data = r['data']
            logger.info("请求校验数据 {}".format(data))
            if pipeline is not None:
                result = pipeline.validate_transforms(cfgs, data)
                logger.info("函数校验结果 {}".format(result))
                resp = message.CommonResponse(200, "validate", '', result)
                return jsonify(resp())
            else:
                return jsonify(message.err_invalid_validate_request())
        except Exception as e:
            stack_info = traceback.format_exc()
            resp = message.CommonResponse(
                500, "validate", "验证服务处理推理数据错误 {}, stack:\n{}".format(e, stack_info))
            return jsonify(resp())


class Application():
    def __init__(self, name):
        # Set settings
        self.app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                         static_folder=os.path.join(os.path.dirname(__file__), "static"))

        # Set URL handlers
        self.app.add_url_rule(
            f'/{name}', methods=["post"], view_func=MainHandler.as_view(name)
        )

    def __call__(self):
        return self.app


class ValidateService:
    def __init__(self, name, port, path, reporter):
        self.name = name or 'validate'
        self.port = port
        self.PERODIC_INTERVAL = 10 if config.PERODIC_INTERVAL == 0 else config.PERODIC_INTERVAL
        global pipeline
        pipeline = Pipeline(reporter, self.PERODIC_INTERVAL)
        pipeline.importalg(path)
        pipeline.reporter.report(
            message.CommonResponse(200, "validate", '', json.dumps({}, cls=JsonEncoder, ensure_ascii=False)))
        self.app = Application(self.name)()

    def run(self):
        signal.signal(signal.SIGILL, exit_handler)
        self.app.run(host='0.0.0.0', port=self.port)
