import json
import random

import aiohttp
import nacos
import tornado.options
import requests
import py_eureka_client.eureka_client as eureka_client
from lesscode.web.status_code import StatusCode

from lesscode.web.business_exception import BusinessException


async def post(path, data=None,
               base_url=tornado.options.options.data_server,
               result_type="json", pack=False, **kwargs):
    flag = kwargs.pop("flag", True)
    if flag:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Content-Type": "application/json"
            }})
    async with aiohttp.ClientSession() as session:
        flag = kwargs.pop("flag", True)
        if flag:
            async with session.post(base_url + path, json=data, **kwargs) as resp:
                if result_type == "json":
                    result = await resp.json()
                    if not pack:
                        if result.get("status") == "00000":
                            result = result.get("data")
                        else:
                            message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                            raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
                elif result_type == "text":
                    result = await resp.text()
                else:
                    result = await resp.content.read()
                return result
        else:
            async with session.post(base_url + path, data=data, **kwargs) as resp:
                if result_type == "json":
                    result = await resp.json()
                    if not pack:
                        if result.get("status") == "00000":
                            result = result.get("data")
                        else:
                            message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                            raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
                elif result_type == "text":
                    result = await resp.text()
                else:
                    result = await resp.content.read()
                return result


async def get(path, params=None, base_url=tornado.options.options.data_server, result_type="json", pack=False,
              **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + path, params=params, **kwargs) as resp:
            if result_type == "json":
                result = await resp.json()
                if not pack:
                    if result.get("status") == "00000":
                        result = result.get("data")
                    else:
                        message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                        raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
            elif result_type == "text":
                result = await resp.text()
            else:
                result = await resp.content.read()
            return result


def sync_get(path, params=None, base_url=tornado.options.options.data_server, result_type="json", pack=False, **kwargs):
    res = requests.get(base_url + path, params=params, **kwargs)
    if result_type == "json":
        res = res.json()
        if not pack:
            if res.get("status") == "00000":
                res = res.get("data")
            else:
                message = f'ori_message:{res.get("status", "")}, {res.get("message", "未知错误")}'
                raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
    elif result_type == "text":
        res = res.text
    else:
        res = res.content
    return res


def sync_post(path, data=None,
              base_url=tornado.options.options.data_server,
              result_type="json", pack=False, **kwargs):
    flag = kwargs.pop("flag", True)
    if flag:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Content-Type": "application/json"
            }})
        res = requests.post(base_url + path, json=data, **kwargs)
    else:
        res = requests.post(base_url + path, data=data, **kwargs)
    if result_type == "json":
        res = res.json()
        if not pack:
            if res.get("status") == "00000":
                res = res.get("data")
            else:
                message = f'ori_message:{res.get("status", "")}, {res.get("message", "未知错误")}'
                raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
    elif result_type == "text":
        res = res.text
    else:
        res = res.content
    return res


def eureka_request(path="", return_type="json", method="GET", data=None, app_name="DATA_SERVICE", pack=False, **kwargs):
    flag = kwargs.pop("flag", True)
    if flag:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Content-Type": "application/json"
            }})
    res = eureka_client.do_service(app_name=app_name, service=path, return_type=return_type, method=method, data=data,
                                   **kwargs)
    if return_type == "json" and not pack:
        if not pack:
            if res.get("status") == "00000":
                res = res.get("data")
            else:
                message = f'ori_message:{res.get("status", "")}, {res.get("message", "未知错误")}'
                raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
    return res


def eureka_get(path="", data=None, return_type="json", app_name="DATA_SERVICE", pack=False, **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")

    if tornado.options.options.running_env != "local":

        res = eureka_request(path=path, return_type=return_type, method="GET", data=data, app_name=app_name, pack=pack,
                             **kwargs)
    else:
        res = sync_get(path=path, params=data, base_url=base_url,
                       result_type=return_type,
                       pack=pack, **kwargs)
    return res


def eureka_post(path="", data=None, return_type="json", app_name="DATA_SERVICE", pack=False, **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":

        res = eureka_request(path=path, return_type=return_type, method="POST", data=json.dumps(data),
                             app_name=app_name,
                             pack=pack, **kwargs)
    else:
        res = sync_post(path=path, data=data, base_url=base_url,
                        result_type=return_type,
                        pack=pack, **kwargs)
    return res


def nacos_service_instance(service_name, namespace, clusters=None, group_name=None):
    server_addresses = tornado.options.options.nacos_config.get("server_addresses")
    client = nacos.NacosClient(server_addresses=server_addresses, namespace=namespace)
    service = client.list_naming_instance(service_name=service_name, clusters=clusters, group_name=group_name,
                                          healthy_only=True)
    service_hosts = service.get("hosts")
    if service_hosts:
        service_host = random.choice(service_hosts)
        return service_host
    else:
        message = f'ori_message:service_name={service_name} has no healthy instance'
        raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))


def nacos_get(path, params=None, service_name=None, namespace="public", clusters=None, group_name=None,
              pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":
        service_instance = nacos_service_instance(service_name=service_name,
                                                  namespace=namespace, clusters=clusters, group_name=group_name)
        base_url = f'http://{service_instance.get("ip")}:{service_instance.get("port")}'

    res = sync_get(path=path, params=params, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
    return res


def nacos_post(path, data=None, service_name=None, namespace="public", clusters=None, group_name=None,
               pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":
        service_instance = nacos_service_instance(service_name=service_name,
                                                  namespace=namespace, clusters=clusters, group_name=group_name)
        base_url = f'http://{service_instance.get("ip")}:{service_instance.get("port")}'

    res = sync_post(path=path, data=data, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
    return res


def common_get(path, params=None, service_name=None, namespace="public", clusters=None, group_name=None,
               pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.request_type == "request":
        res = sync_get(path=path, params=params, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "eureka":
        res = eureka_get(path=path, data=params, return_type=return_type, app_name=service_name, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "nacos":
        res = nacos_get(path=path, params=params, service_name=service_name, namespace=namespace, clusters=clusters,
                        group_name=group_name, pack=pack, return_type=return_type, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)


def common_post(path, data=None, service_name=None, namespace="public", clusters=None, group_name=None,
                pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.request_type == "request":
        res = sync_post(path=path, data=data, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "eureka":
        res = eureka_post(path=path, data=data, return_type=return_type, app_name=service_name, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "nacos":
        res = nacos_post(path=path, data=data, service_name=service_name, namespace=namespace, clusters=clusters,
                         group_name=group_name,
                         pack=pack, return_type=return_type, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)
