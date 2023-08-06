#!/usr/bin/env python
# coding: utf-8
import traceback

import requests
import json

from intelliw.config import config
from intelliw.utils.logger import get_logger
logger = get_logger()


class Report:
    def __init__(self):
        pass

    def report(self, msg):
        print(msg)
        return None


class RestReport:
    def __init__(self, addr, mode='async', local=True):
        self.addr = addr
        self.is_async = True if mode == 'async' else False
        self.is_local = local
        self.seq = 0

    def report(self, msg):
        if hasattr(type(msg), '__str__'):
            data = str(msg)
        else:
            data = json.dumps(msg, ensure_ascii=False)
        self.seq += 1
        trace_id = config.SERVICE_ID + '_p' + str(self.seq)
        if self.addr is not None:
            try:
                s = requests.session()
                headers = {'Content-Type': 'application/json',
                           'X-traceId': trace_id, 'X-tenantId': config.TENANT_ID}
                response = s.post(self.addr, headers=headers,
                                  data=data.encode('utf-8'), verify=False)
                if self.is_local:
                    logger.info('{}, trace_id: {} \nrequest: {} \nresponse: {}'.format(
                        response, trace_id, data, str(response.content)))
            except Exception as e:
                stack_info = traceback.format_exc()
                logger.error("failed to report, url: [{}], request: [{}], exception: [{}], stack:\n{}".
                             format(self.addr, data, e, str(stack_info)))
