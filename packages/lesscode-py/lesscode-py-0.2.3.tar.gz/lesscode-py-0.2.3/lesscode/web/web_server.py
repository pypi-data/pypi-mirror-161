# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/11 8:06 下午
# Copyright (C) 2021 The lesscode Team
import os
import sys
import logging
import tornado.web
import tornado.ioloop
import tornado.httpserver
from apscheduler.schedulers.tornado import TornadoScheduler
from tornado.log import LogFormatter as TornadoLogFormatter  # 避免命名歧义，设置了别名
from tornado.options import options, define
from typing import Optional

from tornado_sqlalchemy import SQLAlchemy

from lesscode.db.init_connection_pool import InitConnectionPool
from lesscode.web.router_mapping import RouterMapping

define("application_name", default=f"{os.path.split(os.path.dirname(sys.argv[0]))[-1]}", type=str, help="配置文件")
define("application_path", default=f"{os.path.dirname(sys.argv[0])}", type=str, help="应用运行根路径")
define("cookie_secret", default="hRHQlJoUQIiNai2MLV9fQV3YDpxWrUHQp/jnfF9riQk=", type=str, help="cookie 秘钥 ")
define("static_path", default=os.path.join(f"{os.path.dirname(sys.argv[0])}", "static"), type=str, help="静态资源目录")
define("aes_key", default="haohaoxuexi", type=str, help="aes加密key")
define("data_server", default="http://127.0.0.1:8901", type=str, help="数据服务")
define("profile", default="profiles.config", type=str, help="配置文件")
define("port", default="8080", type=int, help="服务监听端口")
define("handler_path", default="handlers", type=str, help="处理器文件存储路径")
define("echo_sql", default=True, type=bool, help="是否启用SQL输出")
define("async_enable", default=False, type=bool, help="是否启用异步")
define("max_limit", default=500, type=int, help="单次查询最大数量")
define("eureka_config", default={}, type=dict, help="eureka配置")
define("rms_register_enable", default=False, type=bool, help="是否启动资源注册")
define("rms_register_server", default="http://127.0.0.1:8918", type=str, help="启动资源注册")
define("running_env", default="local", type=str, help="运行环境")
define("request_type", default="request", type=str, help="请求类型")
define("db", default=SQLAlchemy(), type=SQLAlchemy, help="SqlAlchemy")
define("ks3_connect_config", default={}, type=dict, help="金山对象存储连接配置")
define("scheduler", default=None, type=TornadoScheduler, help="Tornado任务调度")
define("scheduler_config", default={}, type=dict, help="Tornado任务调度配置")
define("nacos_config", default={}, type=dict, help="nacos配置")
# 日志初始化配置，配置文件中可修改设置
options.logging = "DEBUG"
options.log_rotate_mode = "time"
options.log_file_prefix = "log"
options.log_rotate_when = "D"
options.log_file_num_backups = 30

options.running_env = "local"


class LogFormatter(TornadoLogFormatter):
    """
    LogFormatter 类用于日志统一格式化处理
    """

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d]%(end_color)s [%(message)s]',
            datefmt='%Y-%m-%d %H:%M:%S')


# 应用实例
def init_log():
    """
    初始化日志配置，创建控制台日志输出处理类，统一设置格式
    :return:
    """
    console_log = logging.StreamHandler()  # 创建控制台日志输出处理类
    console_log.setLevel(options.logging)  # 设置日志级别
    logging.getLogger().handlers.append(console_log)
    # 为日志处理类指定统一的日志输出格式
    [handler.setFormatter(LogFormatter()) for handler in logging.getLogger().handlers]


def load_profile():
    """
    初始化配置文件，配置文件可通过命令行参数指定 --profile=dev
    :return:
    """
    command_profile_flag = False  # 标识配置文件是否通过命令行参数指定
    # 获取命令行参数，此处仅获取profile配置信息
    profile = [item for item in sys.argv if item.__contains__("--profile=")]
    if profile:  # 如果有指定配置文件，更新参数，如果指定多次，取最后一次
        options.profile = f"profiles.config_{profile[-1].replace('--profile=', '')}"
        command_profile_flag = True
    # 第一次加载配置文件
    try:
        __import__(options.profile)
        # command_profile_flag  是False 表示加载的是默认配置文件，还需要再一次判断默认文件中是否指定了其他配置文件，此判断仅针对默认配置文件，其他配置文件不在进行判断。
        if not command_profile_flag and options.profile != "profiles.config":
            __import__(f"profiles.config_{options.profile}")
    except ModuleNotFoundError:
        # 如果加载失败直接跳过，继续执行，给予WARNING。
        logging.warning(f"配置文件不存在：{options.profile}")


class WebServer:
    """
    Wbe服务对象
    """

    def __init__(self):
        load_profile()  # 1、优先处理加载配置文件，要在命令行解析参数前
        tornado.options.parse_command_line()  # 2、调用tornado的命令行参数解析
        init_log()  # 3、初始化日志配置，要在命令行解析参数后，确保日志参数都已经设置完成。
        # 4、启动时创建数据库连接池
        if options.async_enable:
            tornado.ioloop.IOLoop.current().run_sync(InitConnectionPool.create_pool)
        else:
            InitConnectionPool.sync_create_pool()
        # 5、自动化注册Handler处理类，
        self.autoRegisterHandler(f"{os.path.abspath(os.path.dirname(sys.argv[0]))}/{options.handler_path}",
                                 options.handler_path)
        self.autoRegisterExtendHandler()
        if options.scheduler_config.get("enable", False):
            self.init_scheduler()
        self.app = tornado.web.Application(
            RouterMapping.instance(),
            cookie_secret=options.cookie_secret,
            static_path=options.static_path,
            db=options.db,
            debug=True if options.logging == "DEBUG" else False  # 依据日志记录级别确认是否开启调试模式
        )
        self.server = tornado.httpserver.HTTPServer(self.app, max_buffer_size=500 * 1024 * 1024, xheaders=True)  # 500M

    def start(self, num_processes: Optional[int] = 1, max_restarts: int = None):
        if options.eureka_config.get("enable"):
            import py_eureka_client.eureka_client as eureka_client
            eureka_instance_name = options.eureka_config.get("instance_name") if options.eureka_config.get(
                "instance_name") else options.application_name
            eureka_instance_ip = options.eureka_config.get("instance_ip") if options.eureka_config.get(
                "instance_ip") else "127.0.0.1"
            eureka_instance_port = options.eureka_config.get("instance_port") if options.eureka_config.get(
                "instance_port") else options.port
            eureka_client.init(eureka_server=options.eureka_config.get("eureka_server"),
                               app_name=eureka_instance_name,
                               instance_ip=eureka_instance_ip,
                               instance_port=eureka_instance_port)
        if options.nacos_config.get("enable"):
            import nacos
            nacos_service_name = options.nacos_config.get("service_name") if options.nacos_config.get(
                "service_name") else options.application_name
            nacos_namespace = options.nacos_config.get("namespace") if options.nacos_config.get(
                "namespace") else "public"
            nacos_instance_ip = options.nacos_config.get("instance_ip") if options.nacos_config.get(
                "instance_ip") else "127.0.0.1"
            nacos_instance_port = options.nacos_config.get("instance_port") if options.nacos_config.get(
                "instance_port") else options.port
            nacos_instance_weight = options.nacos_config.get("instance_weight") if options.nacos_config.get(
                "instance_weight") else 1.0
            nacos_instance_enable = options.nacos_config.get("instance_enable") if options.nacos_config.get(
                "instance_enable") else True
            nacos_instance_healthy = options.nacos_config.get("instance_healthy") if options.nacos_config.get(
                "instance_healthy") else True
            nacos_instance_ephemeral = options.nacos_config.get("instance_ephemeral") if options.nacos_config.get(
                "instance_ephemeral") else False
            nacos_instance_group_name = options.nacos_config.get("instance_group_name") if options.nacos_config.get(
                "instance_group_name") else "DEFAULT_GROUP"
            nacos_client = nacos.NacosClient(server_addresses=options.nacos_config.get("server_addresses"),
                                             namespace=nacos_namespace,
                                             endpoint=options.nacos_config.get("endpoint"),
                                             ak=options.nacos_config.get("ak"), sk=options.nacos_config.get("sk"),
                                             username=options.nacos_config.get("username"),
                                             password=options.nacos_config.get("password"))
            nacos_client.add_naming_instance(service_name=nacos_service_name, ip=nacos_instance_ip,
                                             port=nacos_instance_port,
                                             cluster_name=options.nacos_config.get("cluster_name"),
                                             weight=nacos_instance_weight,
                                             metadata=options.nacos_config.get("instance_metadata"),
                                             enable=nacos_instance_enable, healthy=nacos_instance_healthy,
                                             ephemeral=nacos_instance_ephemeral, group_name=nacos_instance_group_name)
        self.server.listen(options.port)
        self.server.start(num_processes, max_restarts)
        logging.info(f"start server : {options.application_name}")
        logging.info(f"start server port : {options.port}")
        try:
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            pass
        finally:
            # 关掉连接池
            for item in options.database.items():
                if hasattr(item[1][0], "close"):
                    tornado.ioloop.IOLoop.current().run_sync(item[1][0].close)
        return self

    def autoRegisterHandler(self, path, pkg_name):
        """
        动态注册Handler模块
        遍历项目指定包内的Handler，将包内module引入。
        :param path: 项目内Handler的文件路径
        :param pkg_name: 引入模块前缀
        """
        # 首先获取当前目录所有文件及文件夹
        dynamic_handler_names = os.listdir(path)
        for handler_name in dynamic_handler_names:
            # 利用os.path.join()方法获取完整路径
            full_file = os.path.join(path, handler_name)
            # 循环判断每个元素是文件夹还是文件
            if os.path.isdir(full_file):
                # 文件夹递归遍历
                self.autoRegisterHandler(os.path.join(path, handler_name), ".".join([pkg_name, handler_name]))
            elif os.path.isfile(full_file) and handler_name.lower().endswith("handler.py"):
                # 文件，并且为handler结尾，认为是请求处理器，完成动态装载
                ft = "{}.{}".format(pkg_name, handler_name.replace(".py", ""))
                __import__("{}.{}".format(pkg_name, handler_name.replace(".py", "")))

    def autoRegisterExtendHandler(self):
        # 首先获取当前目录所有文件及文件夹
        import lesscode
        path = f"{os.path.abspath(os.path.dirname(lesscode.__file__))}/extend_handlers"
        pkg_name = "lesscode.extend_handlers"
        dynamic_handler_names = os.listdir(path)
        for handler_name in dynamic_handler_names:
            # 利用os.path.join()方法获取完整路径
            full_file = os.path.join(path, handler_name)
            # 循环判断每个元素是文件夹还是文件
            if os.path.isdir(full_file):
                # 文件夹递归遍历
                self.autoRegisterHandler(os.path.join(path, handler_name), ".".join([pkg_name, handler_name]))
            elif os.path.isfile(full_file) and handler_name.lower().endswith("handler.py"):
                # 文件，并且为handler结尾，认为是请求处理器，完成动态装载
                __import__("{}.{}".format(pkg_name, handler_name.replace(".py", "")))

    def init_scheduler(self):
        options.scheduler = TornadoScheduler(gconfig=options.scheduler_config.get("config", {}),
                                             **options.scheduler_config.get("options", {}))
        options.scheduler.start()
        logging.info('[Scheduler Init]APScheduler has been started')
