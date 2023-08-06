from pydb3.sql.generator.public import PublicGenerator
from pydb3.config.weight import *
from pydb3.utils.valid import table_valid


class DeleteGenerator(PublicGenerator):
    def __init__(self) -> None:
        super().__init__()

    @table_valid
    def delete(self, table):
        self._sql = None
        self.op_dict[OP_WEIGHT] = "DELETE"
        self.op_dict[DELETE_FROM_WEIGHT] = "FROM"
        self.op_dict[DELETE_TABLE_WEIGHT] = f"`{table}`"
        return self

    def execute(self):
        raise NotImplemented

    def __repr__(self):
        return '删除操作'


if __name__ == "__main__":
    deleter = DeleteGenerator()
    deleter.delete("test").where(a=1, b=2).and_()
    print(deleter.sql)
