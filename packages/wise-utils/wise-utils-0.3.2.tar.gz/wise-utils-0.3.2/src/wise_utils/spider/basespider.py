# -*- coding: utf-8 -*-
"""
基于selenium的爬虫类
"""
import urllib3

from wise_utils.common import get_logger

urllib3.disable_warnings()


class BaseSpider:
    def __init__(self, task_name, log_file_path=None, log_level="DEBUG"):
        self.task_name = task_name.lower()
        self.logger = get_logger(name=task_name, path=log_file_path, log_level=log_level)

    def get_proxy_ip(self):
        return {"http": "http://", "https": "http://"}
