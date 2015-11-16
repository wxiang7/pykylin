from __future__ import absolute_import

from sqlalchemy import types as sqltypes
from sqlalchemy.types import INTEGER, BIGINT, SMALLINT, VARCHAR, CHAR, \
    FLOAT, DATE, BOOLEAN

class DOUBLE(sqltypes.Float):
    __visit_name__ = 'DOUBLE'


class TINYINT(sqltypes.Integer):
    __visit_name__ = "TINYINT"


KYLIN_TYPE_MAP = {
    'TINYINT': TINYINT,
    'BIGINT': BIGINT,
    'BOOLEAN': BOOLEAN,
    'CHAR': CHAR,
    'DATE': DATE,
    'DOUBLE': DOUBLE,
    'INT': INTEGER,
    'INTEGER': INTEGER,
    'FLOAT': FLOAT,
    'SMALLINT': SMALLINT,
    'VARCHAR': VARCHAR,
}
