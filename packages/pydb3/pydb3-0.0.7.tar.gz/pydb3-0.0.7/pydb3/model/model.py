import datetime

from pydb3.config.property import FieldProperty
from pydb3.sql.generator.table import TableGenerator
import openpyxl

other = ("__module__", "__main__", "__init__", "__doc__", "db", 'table')


class Model:
    db = None
    table = None

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
                field_unique = getattr(value, 'unique')
                field_property = FieldProperty(
                    name=key, type=field_type, length=field_length,
                    default=field_default, auto=field_auto,
                    primary=field_primary, null=field_null,
                    comment=field_comment, unique=field_unique
                )
                fields.append(field_property)
        sql = table_generator.create(cls.db.db_type, table_name, fields)
        print(sql)
        cls.db.execute(sql)

    def save(self):
        self.table = self.add_underline(self.__class__.__name__)
        values = list()
        for key, value in self.__class__.__dict__.items():
            if key not in other:
                value = getattr(value, '_value')
                values.append(value)
        self.db.insert(self.table, values).execute()

    @classmethod
    def find(cls, **kwargs) -> list:
        cls.table = cls.add_underline(cls.__name__)
        items = list()
        results = cls.db.select(cls.table).where(**kwargs).execute().results
        fields = tuple(filter(lambda x: x not in other, cls.__dict__.keys()))
        for result in results:
            obj = super().__new__(cls, **kwargs)
            for i in range(len(result)):
                try:
                    setattr(obj, fields[i], result[i])
                except Exception as e:
                    raise ValueError(f'{fields[i]}属性设置出错! {e}')
            items.append(obj)
        return items

    @classmethod
    def export_excel(cls, excel_path, models):
        wb = openpyxl.Workbook()
        sheet = wb.create_sheet(cls.__name__.lower())
        titles = [key for key in cls.__dict__.keys() if key not in other]
        sheet.append(titles)
        for m in models:
            item = [getattr(m, t) for t in titles]
            sheet.append(item)
        wb.save(excel_path)

    def __repr__(self):
        fields = list()
        for key, value in self.__class__.__dict__.items():
            if key not in other:
                value = getattr(value, '_value')
                fields.append(f"{key}={value}")
        return f"({','.join(fields)})"
