from datetime import date


class Date:
    type = "date"

    def __init__(self, length=11, default=None, null=False, auto=True, primary=False, comment=None):
        self.length = length
        self.default = default
        self.null = null
        self.primary = primary
        self.comment = comment
        self.auto = auto
        self._value = None

    def __len__(self):
        return self.length

    def __set__(self, instance, value):
        if not value and self.auto:
            self._value = date.today()
        elif isinstance(value, str):
            value = value.replace(" ", "-").replace(",", "-")
            dates = value.split("-")
            if len(dates) < 3:
                raise ValueError("日期不正确!")
            year, month, day = map(int, dates)
            self._value = date(year, month, day)
        elif isinstance(value, date):
            self._value = date
        elif value:
            raise TypeError("日期类型不正确!")

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        del self._value
