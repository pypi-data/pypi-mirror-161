from pydb3.config import *
from pydb3.generator.public import PublicGenerator
from pydb3.utils.valid import table_valid


class SelectGenerator(PublicGenerator):
    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, s: slice):
        size = s.stop - s.start
        return self.limit(s.start, size)

    @table_valid
    def select(self, table=None, *fields):
        self._sql = None
        self.op_dict = dict()
        self.op_dict[OP_WEIGHT] = 'SELECT'
        self.op_dict[SELECT_TABLE_WEIGHT] = f"`{table}`"
        select_fields = "*"
        if len(fields) > 0:
            select_fields = ",".join(fields)
        self.op_dict[SELECT_FIELD_WEIGHT] = select_fields
        self.op_dict[SELECT_FROM_WEIGHT] = 'FROM'
        return self

    def execute(self) -> DBCard:
        raise NotImplemented

    def limit(self, begin=0, size=0):
        self.op_dict[SELECT_LIMIT_WEIGHT] = "LIMIT"
        self.op_dict[SELECT_LIMIT_VALUE_WEIGHT] = f"{begin},{size}"
        return self

    def order_by(self, fields, desc=False):
        try:
            fields = tuple(fields.replace(' ', '').replace(",", " ").split())
        except:
            fields = tuple(fields)
        self.op_dict[SELECT_ORDER_WEIGHT] = 'ORDER BY'
        self.op_dict[SELECT_ORDER_FIELD_WEIGHT] = ','.join(fields)
        self.op_dict[SELECT_ORDER_ASC_WEIGHT] = 'ASC' if not desc else 'DESC'
        return self

    def group_by(self, fields):
        try:
            fields = tuple(fields.replace(' ', '').replace(",", " ").split())
        except:
            fields = tuple(fields)
        self.op_dict[SELECT_GROUP_WEIGHT] = 'GROUP BY'
        self.op_dict[SELECT_GROUP_FIELD] = ','.join(fields)
        return self

    def having(self, equal_op='=', condition='AND', **kwargs):
        return self.where(equal_op, condition, True, **kwargs)


if __name__ == "__main__":
    select = SelectGenerator()
    select.select
