from functools import wraps


def log(name):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            write_path = f"{__file__}/../{name}.log"
            db_card = func(*args, **kwargs)
            with open(write_path, "a", encoding="utf-8") as fp:
                fp.write(db_card.log + "\n")
            return db_card
        return inner
    return wrapper
