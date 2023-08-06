# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
import asyncio

import pymysql
from dbutils.pooled_db import PooledDB
from tornado.options import options, define
from sqlalchemy import create_engine

from lesscode.db.base_connection_pool import BaseConnectionPool
import aiomysql


class SqlAlchemyPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    def sync_create_pool(self):
        db_type = "mysql"
        if self.conn_info.params:
            if self.conn_info.params.get("db_type"):
                db_type = self.conn_info.params.get("db_type")
        if db_type == "mysql":
            url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        elif db_type == "postgresql":
            url = 'postgresql+psycopg2://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        else:
            raise Exception("UNSUPPORTED DB TYPE")
        engine = create_engine(url, echo=True, pool_size=self.conn_info.min_size, pool_recycle=3600,
                               max_overflow=0, pool_timeout=10, pool_pre_ping=True)
        return engine
