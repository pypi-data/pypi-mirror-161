class Char:
    type = "char"

    def __init__(self, length=8, default=None, null=False,
                 primary=False, comment=None, unique=False):
        self.length = length
        self.default = default
        self.null = null
        self.primary = primary
        self.comment = comment
        self.unique = unique
        self.auto = False
        self._value = None

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if self.default:
            self._value = self.default

        elif not self.null and value is None:
            raise ValueError("不能为空!")

        elif not isinstance(value, str):
            raise TypeError(f"{value}必须是字符串!")
        elif len(value) > self.length:
            raise ValueError("字符串超出长度!")
        else:
            self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
