from collections import namedtuple

DBCard = namedtuple("DBCard", "results log status")
FieldProperty = namedtuple("FieldProperty", "name type length auto default null primary comment")

SQLITE_TYPE_MAP = {
    "char": "char",
    "integer": "integer",
    "float": "float",
    "double": "double",
    "text": "text",
    "varchar": "varchar",
    "date": "date",
    "datetime": "datetime",
    'blob': 'blob',
    'image': 'blob'
}

DB_FIELD_MAP = {
    'sqlite': SQLITE_TYPE_MAP
}
