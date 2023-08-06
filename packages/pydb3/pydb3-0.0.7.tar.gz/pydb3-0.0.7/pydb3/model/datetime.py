from _datetime import datetime
import time


class DateTime:
    type = "datetime"

    def __init__(self, default=None, null=False, auto=True, primary=False, comment=None, unique=False):
        self.length = None
        self.default = default
        self.null = null
        self.primary = primary
        self.comment = comment
        self.auto = auto
        self.unique = unique
        self._value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __len__(self):
        return 19

    def __set__(self, instance, value):
        if not value and self.auto:
            self._value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, str):
            value = time.strftime(value)
            self._value = value
        elif isinstance(value, datetime):
            self._value = value
        elif value:
            raise TypeError("时间类型不正确!")

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value


if __name__ == '__main__':
    print(len('2022-08-13 00:00:00'))
