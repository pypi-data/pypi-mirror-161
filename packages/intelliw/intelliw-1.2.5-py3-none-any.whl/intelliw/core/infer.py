'''
Author: Hexu
Date: 2022-03-14 09:53:59
LastEditors: Hexu
LastEditTime: 2022-05-26 14:54:26
FilePath: /iw-algo-fx/intelliw/core/infer.py
Description: 
'''
# coding: utf-8
from intelliw.interface.apihandler import Request
from intelliw.core.pipeline import Pipeline


class Infer:
    def __init__(self, path, reporter=None, perodic_interval=-1):
        self.pipeline = Pipeline(reporter, perodic_interval)
        self.pipeline.importmodel(path)

    def infer(self, data, request=Request(), func='infer', need_featrue=True):
        return self.pipeline.infer(data, request, func, need_featrue)

    def perodic_callback(self):
        self.pipeline.perodic_callback_infer()
