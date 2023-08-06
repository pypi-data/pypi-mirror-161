from typing import Sequence
from pydb3.config.weight import *
from pydb3.sql.generator.public import Filter
from pydb3.utils.valid import table_valid, data_valid


class InsertGenerator:
    def __init__(self) -> None:
        self.op_dict = dict()
        self._sql = None

    @table_valid
    @data_valid('insert')
    def insert(self, table, fields: Sequence):
        self._sql = None
        self.op_dict[OP_WEIGHT] = 'INSERT INTO'
        self.op_dict[INSERT_TABLE_WEIGHT] = f"`{table}`"
        fields = [Filter.map(field, True) for field in fields]
        values = ",".join(fields)
        self.op_dict[INSERT_VALUES_WEIGHT] = f"VALUES({values})"
        return self

    @property
    def sql(self):
        if self._sql:
            return self._sql
        else:
            op_dict = sorted(self.op_dict.items(), key=lambda a: a[0])
            self._sql = " ".join([op[1] for op in op_dict])
            return self._sql

    def execute(self):
        raise NotImplemented

    def __repr__(self):
        return '插入操作'


if __name__ == "__main__":
    inserter = InsertGenerator()
    inserter.insert("test", [])
