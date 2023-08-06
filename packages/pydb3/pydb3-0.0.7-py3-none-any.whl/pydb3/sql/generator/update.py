from pydb3.config.weight import *
from pydb3.sql.generator.public import PublicGenerator, Filter
from pydb3.utils.valid import table_valid, data_valid


class UpdateGenerator(PublicGenerator):
    def __init__(self) -> None:
        super().__init__()

    @table_valid
    @data_valid("update")
    def update(self, table, **kwargs):
        if not kwargs:
            raise ValueError("更新参数为空!")
        self.op_dict[OP_WEIGHT] = 'UPDATE'
        self.op_dict[UPDATE_TABLE_WEIGHT] = f"`{table}`"
        self.op_dict[UPDATE_SET_WEIGHT] = "SET"
        self.op_dict[UPDATE_SET_FIELD_WEIGHT] = ",".join(
            [f"`{key}` = {Filter.map(value)}" for key, value in kwargs.items()])
        return self

    def execute(self):
        raise NotImplemented

    def __repr__(self):
        return '更新操作'


if __name__ == "__main__":
    updater = UpdateGenerator()
    updater.update("student", name=None, age=12, gender='男').where(name=12, age=13) | updater.where(
        a=123) | updater.like(b=1234)
    print(updater.sql)
