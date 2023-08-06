import pymysql
from typing import Sequence
from functools import wraps
from pydb3.config.property import DBCard
from pydb3.sql.generator.select import SelectGenerator
from pydb3.sql.generator.update import UpdateGenerator
from pydb3.sql.generator.delete import DeleteGenerator
from pydb3.sql.generator.insert import InsertGenerator
from pydb3.log.log import log


def mysql_execute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        connect_args, sql, executor = func(*args, **kwargs)
        results = []
        conn = pymysql.connect(
            host=connect_args['host'], port=connect_args['port'],
            database=connect_args['database'], password=connect_args['password'],
            user=connect_args['user']
        )
        sql = sql or executor.sql
        msg = f"{executor}成功!--{sql}"
        status = 1
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            msg = f"{e}--{sql}"
            status = 0
        if str(executor) == '查询操作':
            results = cursor.fetchall()
        db_card = DBCard(results=results, log=msg, status=status)
        return db_card

    return wrapper


class Mysql:
    def __init__(self,
                 host='127.0.0.1', port='3306', database='db',
                 user='root', password='123456'
                 ) -> None:
        self.selector = SelectGenerator()
        self.updater = UpdateGenerator()
        self.deleter = DeleteGenerator()
        self.inserter = InsertGenerator()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.operator = None

    def select(self, table=None, *fields) -> SelectGenerator:
        self.operator = self.selector
        self.operator.execute = self.execute
        return self.operator.select(table, *fields)

    def update(self, table, **kwargs) -> UpdateGenerator:
        self.operator = self.updater
        self.operator.execute = self.execute
        return self.operator.update(table, **kwargs)

    def insert(self, table, fields: Sequence) -> InsertGenerator:
        self.operator = self.inserter
        self.operator.execute = self.execute
        return self.operator.insert(table, fields)

    def delete(self, table) -> DeleteGenerator:
        self.operator = self.deleter
        self.operator.execute = self.execute
        return self.operator.delete(table)

    @log(name="mysql", command=True, file=True)
    @mysql_execute
    def execute(self, sql=None):
        connect_args = dict(
            host=self.host, port=int(self.port), user=self.user,
            database=self.database, password=self.password
        )
        return connect_args, sql, self.operator


if __name__ == '__main__':
    pass
