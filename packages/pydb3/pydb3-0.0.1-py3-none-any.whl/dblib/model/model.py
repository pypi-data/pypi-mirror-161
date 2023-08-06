from pydb3.config import FieldProperty
from pydb3.generator.table import TableGenerator
from pydb3.generator.update import UpdateGenerator
from pydb3.generator.delete import DeleteGenerator
from pydb3.generator.select import SelectGenerator

other = ("__module__", "__main__", "__init__", "__doc__", "db")


class Model:
    db = None

    @classmethod
    def set_db(cls, db):
        cls.db = db

    @classmethod
    def add_underline(cls, class_name) -> str:
        count = 0
        ch_list = list()
        for ch in class_name:
            if 'A' <= ch <= 'Z':
                count += 1
                if count > 1:
                    ch_list.append("_")
            ch_list.append(ch)
        class_name = "".join(ch_list)
        return class_name.lower()

    @classmethod
    def create_table(cls):
        table_generator = TableGenerator()
        table_name = cls.add_underline(cls.__name__)
        fields = list()
        for key, value in cls.__dict__.items():
            if key not in other:
                field_length = getattr(value, "length")
                field_type = getattr(value, "type")
                field_default = getattr(value, "default")
                field_auto = getattr(value, "auto") if hasattr(value, "auto") else False
                field_primary = getattr(value, "primary")
                field_null = getattr(value, "null")
                field_comment = getattr(value, 'comment')
                field_property = FieldProperty(
                    name=key, type=field_type, length=field_length,
                    default=field_default, auto=field_auto,
                    primary=field_primary, null=field_null,
                    comment=field_comment
                )
                fields.append(field_property)
        sql = table_generator.create(cls.db.db_type, table_name, fields)
        print(sql)
        cls.db.execute(sql)

    def save(self):
        values = list()
        table_name = self.add_underline(self.__class__.__name__)
        for key, value in self.__class__.__dict__.items():
            if key not in other:
                value = getattr(value, '_value')
                values.append(value)
        self.db.insert(table_name, values).execute()

    @classmethod
    def update(cls, table, **kwargs) -> UpdateGenerator:
        cls.db.update(table, **kwargs)

    @classmethod
    def delete(cls, table) -> DeleteGenerator:
        cls.db.delete(table).execute()

    @classmethod
    def select(cls, table, **kwargs) -> SelectGenerator:
        cls.db.select(table, **kwargs)

    def __repr__(self):
        fields = list()
        for key, value in self.__class__.__dict__.items():
            if key not in other:
                value = getattr(value, '_value')
                fields.append(f"{key}={value}")
        return f"({','.join(fields)})"
