from sqlalchemy.orm import Session
from tornado.options import options


class SqlAlchemyHelper:
    def __init__(self, pool):
        """
        初始化sql工具
        :param pool: 连接池名称
        """
        if isinstance(pool, str):
            self.pool, self.dialect = options.database[pool]
        else:
            self.pool = pool

    def make_session(self):
        session = Session(self.pool)
        return session
