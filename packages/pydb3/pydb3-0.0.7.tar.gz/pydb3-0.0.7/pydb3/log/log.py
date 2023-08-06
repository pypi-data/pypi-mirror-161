import os
from functools import wraps


def log(name, command=False, file=True, level=0):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            write_path = f"{os.getcwd()}/{name}.log"
            db_card = func(*args, **kwargs)
            if command and (level or level == db_card.status):
                print(db_card.log)
            if file:
                with open(write_path, "a", encoding="utf-8") as fp:
                    fp.write(db_card.log + "\n")
            return db_card
        return inner

    return wrapper
