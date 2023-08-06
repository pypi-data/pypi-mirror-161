class Integer:
    _value = 0
    type = "integer"

    def __init__(self, length=11, default=None, null=False, auto=False, primary=False, comment=None):
        self.length = length
        self.default = default
        self.null = null
        self.primary = primary
        self.auto = auto
        self.comment = comment

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if not value and self.auto:
            self._value += 1
        elif self.default:
            self._value = self.default
        elif not self.null and value is None:
            raise ValueError("不能为空!")
        elif not isinstance(value, int):
            raise TypeError(f"{value}必须是整数!")
        elif len(str(value)) > self.length:
            raise ValueError("整形超出长度!")
        else:
            self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
