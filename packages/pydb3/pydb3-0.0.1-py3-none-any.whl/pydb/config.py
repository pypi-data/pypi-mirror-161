from collections import namedtuple

OP_WEIGHT = 0
WHERE_WEIGHT = 2.5
CONDITION_WEIGHT = 3

SELECT_FIELD_WEIGHT = 1
SELECT_FROM_WEIGHT = 2
SELECT_TABLE_WEIGHT = 2.2

SELECT_GROUP_WEIGHT = 2.6
SELECT_GROUP_FIELD = 2.7

SELECT_HAVING_WEIGHT = 2.8
SELECT_HAVING_CONDITION = 2.9

SELECT_ORDER_WEIGHT = 4
SELECT_ORDER_FIELD_WEIGHT = 5
SELECT_ORDER_ASC_WEIGHT = 6

SELECT_LIMIT_WEIGHT = 7
SELECT_LIMIT_VALUE_WEIGHT = 8

UPDATE_TABLE_WEIGHT = 1
UPDATE_SET_WEIGHT = 1.5
UPDATE_SET_FIELD_WEIGHT = 2

INSERT_TABLE_WEIGHT = 1
INSERT_VALUES_WEIGHT = 2

DELETE_FROM_WEIGHT = 1
DELETE_TABLE_WEIGHT = 2

CREATE_TABLE_WEIGHT = 1
CREATE_TABLE_FIELD_WEIGHT = 2
CREATE_TABLE_FIELDS_WEIGHT = 3

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
    "datetime": "datetime"
}

DB_FIELD_MAP = {
    'sqlite': SQLITE_TYPE_MAP
}
