class Float:
    type = "float"

    def __init__(self, length=11, default=None, null=False, primary=False, comment=None, unique=False):
        self.length = length
        self.default = default
        self.null = null
        self.primary = primary
        self.auto = False
        self.comment = comment
        self.unique = unique

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if self.default:
            self._count = self.default

        elif not self.null and value is None:
            raise ValueError("不能为空!")

        elif not isinstance(value, float) and value:
            raise TypeError("必须为浮点数!")
        elif len(str(value)) > self.length:
            raise ValueError("该数超出长度!")
        else:
            self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
