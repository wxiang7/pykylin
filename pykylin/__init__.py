from __future__ import absolute_import

from .connection import connect
from .errors import *

paramstyle = 'pyformat'
threadsafety = 2

__all__ = [
    'connect', 'apilevel', 'threadsafety', 'paramstyle',
    'Warning', 'Error', 'InterfaceError', 'DatabaseError', 'DataError', 'OperationalError', 'IntegrityError',
    'InternalError', 'ProgrammingError', 'NotSupportedError'
]
