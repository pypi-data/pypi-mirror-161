class Blob:
    type = "blob"

    def __init__(self, null=False, comment=None, unique=False):
        self.length = None
        self.default = None
        self.null = null
        self.primary = False
        self.comment = comment
        self.auto = False
        self.unique = unique
        self._value = None

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if not self.null and value is None:
            raise ValueError("不能为空!")
        elif not isinstance(value, str):
            raise TypeError(f"{value}必须是字符串!")
        else:
            self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
