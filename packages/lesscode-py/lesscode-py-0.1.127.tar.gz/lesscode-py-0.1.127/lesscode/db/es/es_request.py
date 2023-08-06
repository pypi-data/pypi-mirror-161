# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/3/2 9:14 上午
# Copyright (C) 2021 The lesscode Team
import json
import random

import requests
from requests.auth import HTTPBasicAuth


class EsRequest:

    def __init__(self, host, port, user, password):
        # 主机地址
        self.host = host
        # 端口号
        self.port = port
        # 用户名
        self.user = user
        # 密码
        self.password = password
        self.auth = HTTPBasicAuth(user, password)
        host_str = host.split(",")
        self.hosts = [host for host in host_str]

    def es_selector_way(self, url_func_str, param_dict, find_condition):
        res = None
        # 随机打乱列表
        random.shuffle(self.hosts)
        for host in self.hosts:
            param_dict["host"] = host
            param_dict["port"] = self.port
            url = url_func_str(**param_dict)
            try:
                res = self.format_es_post(url, find_condition)
                break
            except:
                continue
        return res

    def format_es_post(self, url, body):
        """
        发送http请求
        :param url:
        :param body:
        :return:
        """
        r = requests.post(
            url,
            data=json.dumps(body),
            headers={'content-type': "application/json"},
            auth=self.auth
        )
        res = r.json()
        return res

    def format_es_put(self, url, body, params=None):
        """
        发送http请求
        :param params:
        :param url:
        :param body:
        :return:
        """
        r = requests.put(
            url,
            params=params,
            data=json.dumps(body),
            headers={'content-type': "application/json"},
            auth=self.auth
        )
        res = r.json()
        return res

    def format_es_get(self, url, params=None):
        """
        发送http请求
        :param params:
        :param url:
        :param body:
        :return:
        """
        r = requests.get(
            url,
            params=params,
            headers={'content-type': "application/json"},
            auth=self.auth
        )
        res = r.json()
        return res

    def format_es_delete(self, url, body=None, params=None):
        """
        发送http请求
        :param params:
        :param url:
        :param body:
        :return:
        """
        r = requests.delete(
            url,
            data=json.dumps(body) if body else body,
            params=params,
            headers={'content-type': "application/json"},
            auth=self.auth
        )
        res = r.json()
        return res

    def format_scroll_url(self, host=None, port=None, route_key=None, scroll=None):
        return "http://{}:{}/{}/_search?scroll={}".format(host if host else self.host,
                                                          port if port else self.port, route_key, scroll)

    def format_scroll_id_url(self, host=None, port=None, ):
        return "http://{}:{}/_search/scroll".format(host if host else self.host,
                                                    port if port else self.port)

    def format_es_post_url(self, host=None, port=None, route_key=None):
        return "http://{}:{}/{}/_search".format(host if host else self.host,
                                                port if port else self.port, route_key)

    def format_url(self, path, host=None, port=None):
        return "http://{}:{}{}".format(host if host else self.host,
                                       port if port else self.port, path)

    def close(self):
        pass
