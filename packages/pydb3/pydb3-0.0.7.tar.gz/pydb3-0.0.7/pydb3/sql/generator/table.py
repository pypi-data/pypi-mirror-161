from typing import Sequence
from pydb3.config.property import *
from pydb3.config.weight import *
from pydb3.utils.valid import table_valid, data_valid


class TableGenerator:
    db_type = None

    def __init__(self):
        self.op_dict = dict()

    @data_valid("create")
    @table_valid
    def create(self, db_type='sqlite', table=None, fields: Sequence = None):
        self.db_type = db_type
        self.op_dict[OP_WEIGHT] = "CREATE TABLE"
        self.op_dict[CREATE_TABLE_WEIGHT] = f"`{table}`"
        for field in fields:
            self.create_field(field)
        return self.sql

    @classmethod
    def type_map(cls, db_type, field):
        return FIELD_TYPE_MAP.get(db_type).get(field)

    def create_field(self, field: FieldProperty):
        field_type = self.type_map(self.db_type, field.type)
        field_length = f'({field.length})' if not field.auto and field.length else ''
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT] = [field.name]
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append(f"{field_type}{field_length}")
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append('UNIQUE' if field.unique else '')
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append('NULL' if field.null else 'NOT NULL')
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append('PRIMARY KEY' if field.primary else '')
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append(
            CREATE_PROPERTY_MAP.get(self.db_type)['auto'] if field.auto else '')
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT].append(f',-- {field.comment}' if field.comment else ',')
        self.op_dict[CREATE_TABLE_FIELD_WEIGHT] = " ".join(self.op_dict[CREATE_TABLE_FIELD_WEIGHT])
        if self.op_dict.get(CREATE_TABLE_FIELDS_WEIGHT):
            self.op_dict[CREATE_TABLE_FIELDS_WEIGHT].append(self.op_dict[CREATE_TABLE_FIELD_WEIGHT])
        else:
            self.op_dict[CREATE_TABLE_FIELDS_WEIGHT] = [self.op_dict[CREATE_TABLE_FIELD_WEIGHT]]

    @property
    def sql(self):
        self.op_dict[CREATE_TABLE_FIELDS_WEIGHT][-1] = self.op_dict[CREATE_TABLE_FIELDS_WEIGHT][-1].replace(',', '')
        self.op_dict[CREATE_TABLE_FIELDS_WEIGHT] = "\n\t".join(self.op_dict[CREATE_TABLE_FIELDS_WEIGHT])
        result = f"{self.op_dict[OP_WEIGHT]} {self.op_dict[CREATE_TABLE_WEIGHT]} (\n\t{self.op_dict[CREATE_TABLE_FIELDS_WEIGHT]}\n); "
        return result
