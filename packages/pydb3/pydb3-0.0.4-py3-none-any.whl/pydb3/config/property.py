from collections import namedtuple

DBCard = namedtuple("DBCard", "results log status")
FieldProperty = namedtuple("FieldProperty", "name type length auto default null primary unique comment")
DBProperty = namedtuple("DBProperty", 'connect_args sql executor')
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
MYSQL_TYPE_MAP = {
    "char": "char",
    "integer": "int",
    "float": "float",
    "double": "double",
    "text": "text",
    "varchar": "varchar",
    "date": "date",
    "datetime": "datetime",
    'blob': 'blob',
    'image': 'blob'
}
FIELD_TYPE_MAP = {
    'sqlite': SQLITE_TYPE_MAP,
    'mysql': MYSQL_TYPE_MAP
}
CREATE_PROPERTY_MAP = {
    'sqlite': {
        'auto': 'AUTOINCREMENT'
    },
    'mysql': {
        'auto': 'AUTO_INCREMENT',
        'unique': 'unique'
    },
}
