from pydb3.config.weight import *


class PublicGenerator:
    def __init__(self):
        self.op_dict = dict()
        self._sql = None

    def and_(self, equal_op='=', **kwargs):
        return self.where(equal_op, 'AND', **kwargs)

    def or_(self, equal_op='=', **kwargs):
        return self.where(equal_op, 'OR', **kwargs)

    def where(self, equal_op='=', condition='AND', is_group=False, **kwargs):
        condition_op_weight = WHERE_WEIGHT if not is_group else SELECT_HAVING_WEIGHT
        condition_op = 'WHERE' if not is_group else 'HAVING'
        condition_weight = CONDITION_WEIGHT if not is_group else SELECT_HAVING_CONDITION
        if kwargs:
            self.op_dict[condition_op_weight] = condition_op
            for key, value in kwargs.items():
                value = Filter.map(value)
                value = f"'%{value}%'" if equal_op == 'LIKE' else value
                condition_str = f"`{key}` {equal_op} {value}"
                if not self.op_dict.get(condition_weight):
                    self.op_dict[condition_weight] = [condition_str]
                else:
                    self.op_dict[condition_weight].append(condition)
                    self.op_dict[condition_weight].append(condition_str)
        return self

    def like(self, **kwargs):
        return self.where('LIKE', **kwargs)

    @property
    def sql(self):
        if self._sql:
            return self._sql
        else:
            if self.op_dict.get(CONDITION_WEIGHT):
                self.op_dict[CONDITION_WEIGHT] = " ".join(self.op_dict[CONDITION_WEIGHT])

            if self.op_dict.get(SELECT_HAVING_CONDITION):
                self.op_dict[SELECT_HAVING_CONDITION] = " ".join(self.op_dict[SELECT_HAVING_CONDITION])

            op_dict = sorted(self.op_dict.items(), key=lambda a: a[0])
            self._sql = " ".join([op[1] for op in op_dict])
            return self._sql


class Filter:
    def __init__(self):
        pass

    @classmethod
    def map(cls, value, insert=False):
        if value is None:
            return "NULL"
        elif isinstance(value, str) or insert:
            return f"'{value}'"
        else:
            return value
