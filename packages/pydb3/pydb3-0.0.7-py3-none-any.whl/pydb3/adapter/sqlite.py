import sqlite3
from typing import Sequence
from functools import wraps
from pydb3.config.property import DBCard, DBProperty
from pydb3.sql.generator.select import SelectGenerator
from pydb3.sql.generator.update import UpdateGenerator
from pydb3.sql.generator.delete import DeleteGenerator
from pydb3.sql.generator.insert import InsertGenerator
from pydb3.log.log import log


def sqlite_execute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        connect_args, sql, executor = func(*args, **kwargs)
        conn = sqlite3.connect(connect_args.get('file_path'))
        sql = sql or executor.sql
        msg = f"{executor}成功!--{sql}"
        status = 1
        results = []
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


class Sqlite:
    def __init__(self, file_path='db.sqlite') -> None:
        self.selector = SelectGenerator()
        self.updater = UpdateGenerator()
        self.deleter = DeleteGenerator()
        self.inserter = InsertGenerator()
        self.file_path = file_path
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

    @log(name="sqlite", command=True, file=True)
    @sqlite_execute
    def execute(self, sql=None) -> DBProperty:
        connect_args = dict(file_path=self.file_path)
        return connect_args, sql, self.operator


if __name__ == '__main__':
    sqlite = Sqlite(r"E:\python\db-library\data\test.db")
    a = sqlite.update("student", name="test").where(name="李白").like(age='%2%').execute()
    print(a)
