class Integer:
    _value = 0
    type = "integer"

    def __init__(self, length=11, default=None, null=False, auto=False, primary=False, comment=None, unique=False):
        self.length = length
        self.default = default
        self.null = null
        self.primary = primary
        self.auto = auto
        self.comment = comment
        self.unique = unique

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if not value:
            self._value = self.default if not self.auto else None
            if not self.null and not self._value and not self.auto:
                raise ValueError("不能为空!")
        else:
            if not isinstance(value, int):
                raise TypeError(f"{value}必须是整数!")
            elif len(str(value)) > self.length:
                raise ValueError("整形超出长度!")
            else:
                self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
