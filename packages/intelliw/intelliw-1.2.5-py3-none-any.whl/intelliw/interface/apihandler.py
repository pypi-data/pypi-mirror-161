'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2022-07-25 16:09:02
LastEditors: Hexu
Description: api处理函数
FilePath: /iw-algo-fx/intelliw/interface/apihandler.py
'''
import time
import json
import traceback
from flask import current_app as app
from flask import request, jsonify, views
import intelliw.utils.message as message
from intelliw.config import config
from intelliw.utils.util import JsonEncoder
from intelliw.utils.logger import get_logger

logger = get_logger()


class Request:
    def __init__(self) -> None:
        self.header = None
        self.json = ""
        self.query = dict()
        self.form = dict()
        self.files = list()
        self.body = ""


class BaseHandler():
    def __init__(self):
        self.infer_request = Request()

    # request
    def request_process(self):
        ok = True
        try:
            self.infer_request.header = request.headers

            # query
            query = request.args.to_dict()
            self.infer_request.query = query

            # body
            self.infer_request.body = request.get_data()
            req_data = {}
            content_type = request.headers.get('Content-Type', "").strip()
            if content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('multipart/form-data'):
                req_data = request.form.to_dict(False)
                self.infer_request.form = req_data
            elif content_type.startswith('application/json'):
                req_data = request.json
                self.infer_request.json = req_data

            # 如果body中没东西，那请求内容可以尝试从query中获取
            if not req_data:
                req_data = query

            # files
            files = []
            if request.files:
                for f in request.files.values():
                    files.extend(f)
            self.infer_request.files = files
        except Exception as e:
            stack = traceback.format_exc()
            req_data = message.APIResponse(
                400, "api", f"API服务请求解析错误: {e}, Body: {str(request.data)}, Stack: {stack}")
            return req_data, not ok
        return req_data, ok

    # response
    def response_process(self, data, func, need_featrue):
        try:
            result, emsg = app.config["infer"].infer(
                data, self.infer_request, func, need_featrue)
            if emsg is None:
                resp = message.APIResponse(200, "api", '', result)
            else:
                resp = message.APIResponse(500, "api", emsg, result)
        except Exception as e:
            self.error_report(e)
            resp = message.APIResponse(
                500, "api", "API服务处理推理数据错误 {}".format(e))
        return resp

    # error report
    def error_report(self, e: Exception):
        stack_info = traceback.format_exc()
        logger.error("API服务处理推理数据错误 {} stack: {}".format(e, stack_info))
        msg = [{'status': 'inferfalied', 'inferid': config.INFER_ID, 'instanceid': config.INSTANCE_ID,
                'inferTaskStatus': [{
                    "id": config.INFER_ID, "issuccess": False,
                    "starttime": int(time.time() * 1000),
                    "endtime": int(time.time() * 1000),
                    "message": "API服务处理推理数据错误"
                }]}]
        app.config["reporter"].report(message.CommonResponse(500, "inferstatus", "API服务处理推理数据错误 {}".format(
            e), json.dumps(msg, cls=JsonEncoder, ensure_ascii=False)))


class HealthCheckHandler(views.MethodView):
    """健康检查"""

    def post(self):
        resp = message.HealthCheckResponse(200, "api", 'ok', "")
        return jsonify(resp())

    def get(self):
        resp = message.HealthCheckResponse(200, "api", 'ok', "")
        return jsonify(resp())


class MainHandler(views.MethodView):
    def get(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def post(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def put(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def delete(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def options(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def patch(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def head(self, func, need_featrue=True):
        return self.__do(func, need_featrue)

    def __do(self, func, need_featrue):
        base = BaseHandler()
        result, ok = base.request_process()
        if ok:
            result = base.response_process(result, func, need_featrue)
        return jsonify(result())
