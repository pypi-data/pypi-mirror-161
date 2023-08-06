import sqlite3
from typing import Sequence
from functools import wraps
from pydb3.config.property import DBCard
from pydb3.generator.select import SelectGenerator
from pydb3.generator.update import UpdateGenerator
from pydb3.generator.delete import DeleteGenerator
from pydb3.generator.insert import InsertGenerator
from pydb3.log.log import log


def sqlite_execute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file_path, sql, selector = func(*args, **kwargs)
        conn = sqlite3.connect(file_path)
        sql = sql or selector.sql
        msg = f"{selector}成功!--{sql}"
        status = 1
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            msg = f"{e}--{sql}"
            status = 0
        db_card = DBCard(results=cursor.fetchall(), log=msg, status=status)
        return db_card

    return wrapper


class Sqlite:
    def __init__(self, file_path="test.db") -> None:
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
    def execute(self, sql=None):
        return self.file_path, sql, self.operator


if __name__ == '__main__':
    sqlite = Sqlite(r"E:\python\db-library\data\test.db")
    a = sqlite.update("student", name="test").where(name="李白").like(age='%2%').execute()
    print(a)
