from __future__ import absolute_import

from dateutil import parser

from .errors import Error
from .log import logger

class Cursor(object):

    def __init__(self, connection):
        self.connection = connection
        self._arraysize = 1

        self.description = None
        self.rowcount = -1
        self.results = None
        self.fetched_rows = 0

    def callproc(self):
        raise('Stored procedures not supported in Kylin')

    def close(self):
        logger.debug('Cursor close called')

    def execute(self, operation, parameters={}, acceptPartial=True, limit=None, offset=0):
        sql = operation % parameters
        data = {
            'sql': sql,
            'offset': offset,
            'limit': limit or self.connection.limit,
            'acceptPartial': acceptPartial,
            'project': self.connection.project
        }
        logger.debug("QUERY KYLIN: %s" % sql)
        resp = self.connection.proxy.post('query', json=data)

        column_metas = resp['columnMetas']
        self.description = [
            [c['label'], c['columnTypeName'],
             c['displaySize'], 0,
             c['precision'], c['scale'], c['isNullable']]
            for c in column_metas
        ]

        self.results = [self._type_mapped(r) for r in resp['results']]
        self.rowcount = len(self.results)
        self.fetched_rows = 0
        return self.rowcount

    def _type_mapped(self, result):
        meta = self.description
        size = len(meta)
        for i in range(0, size):
            column = meta[i]
            tpe = column[1]
            val = result[i]
            if tpe == 'DATE':
                val = parser.parse(val)
            elif tpe == 'BIGINT' or tpe == 'INT' or tpe == 'TINYINT':
                val = int(val)
            elif tpe == 'DOUBLE' or tpe == 'FLOAT':
                val = float(val)
            elif tpe == 'BOOLEAN':
                val = (val == 'true')
            result[i] = val
        return result

    def executemany(self, operation, seq_params=[]):
        results = []
        for param in seq_params:
            self.execute(operation, param)
            results.extend(self.results)
        self.results = results
        self.rowcount = len(self.results)
        self.fetched_rows = 0
        return self.rowcount

    def fetchone(self):
        if self.fetched_rows < self.rowcount:
            row = self.results[self.fetched_rows]
            self.fetched_rows += 1
            return row
        else:
            return None

    def fetchmany(self, size=None):
        fetched_rows = self.fetched_rows
        size = size or self.arraysize
        self.fetched_rows = fetched_rows + size
        return self.results[fetched_rows:self.fetched_rows]

    def fetchall(self):
        fetched_rows = self.fetched_rows
        self.fetched_rows = self.rowcount
        return self.results[fetched_rows:]

    def nextset(self):
        raise Error('Nextset operation not supported in Kylin')

    @property
    def arraysize(self):
        return self._arraysize

    @arraysize.setter
    def arraysize(self, array_size):
        self._arraysize = array_size

    def setinputsizes(self):
        logger.warn('setinputsize not supported in Kylin')

    def setoutputsize(self):
        logger.warn('setoutputsize not supported in Kylin')
