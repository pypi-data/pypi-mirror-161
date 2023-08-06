from pydb3.sql.generator.delete import DeleteGenerator
from pydb3.sql.generator.insert import InsertGenerator
from pydb3.sql.generator.select import SelectGenerator
from pydb3.sql.generator.update import UpdateGenerator
from pydb3.model import Model


class Db:

    def __init__(self, db_type="sqlite", *args, **kwargs) -> None:
        db_class = self.from_db(db_type)
        self.db = db_class(*args, **kwargs)
        self.db_type = db_type

    @classmethod
    def from_db(cls, db_type='sqlite'):
        class_name = db_type.capitalize()
        db_module = __import__(f"pydb3.adapter.{db_type}", fromlist=[class_name])
        db_class = getattr(db_module, class_name)
        return db_class

    def execute(self, sql):
        return self.db.execute(sql)

    def select(self, table=None, *fields) -> SelectGenerator:
        return self.db.select(table, *fields)

    def update(self, table, **kwargs) -> UpdateGenerator:
        return self.db.update(table, **kwargs)

    def delete(self, table) -> DeleteGenerator:
        return self.db.delete(table)

    def insert(self, table, fields) -> InsertGenerator:
        return self.db.insert(table, fields)

    def create_table(self, model: Model):
        model.set_db(self)
        model.create_table()

    @property
    def sql(self):
        return self.db.sql


if __name__ == '__main__':
    db = Db('mysql', host='localhost', port='3306', user='root', database='db', password='123456')
    sql = db.select('student').join('class', id='stu_id').sql
    print(sql)
