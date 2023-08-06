from functools import wraps


def table_valid(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[-1] is None:
            raise ValueError("表名不能为空!")
        return func(*args, **kwargs)

    return wrapper


def data_valid(op):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if op == 'insert' and not args[-1]:
                raise ValueError("无插入数据!")
            elif op == "update" and not kwargs:
                raise ValueError("无更新字段!")
            elif op == "create" and not args[-1]:
                raise ValueError("无创建字段!")
            elif op == 'join' and len(args) < 3:
                raise ValueError("无连接字段!")
            return func(*args, **kwargs)

        return wrapper

    return inner
