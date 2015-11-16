from __future__ import absolute_import

from sqlalchemy import pool
from sqlalchemy.sql.compiler import *
from sqlalchemy.engine import default
from .types import KYLIN_TYPE_MAP

class KylinCompiler(SQLCompiler):

    def visit_label(self, label,
                    add_to_result_map=None,
                    within_label_clause=False,
                    within_columns_clause=False,
                    render_label_as_label=None,
                    **kw):
        # only render labels within the columns clause
        # or ORDER BY clause of a select.  dialect-specific compilers
        # can modify this behavior.
        render_label_with_as = (within_columns_clause and not
        within_label_clause)
        render_label_only = render_label_as_label is label

        if render_label_only or render_label_with_as:
            if isinstance(label.name, elements._truncated_label):
                labelname = self._truncated_identifier("colident", label.name)
            else:
                labelname = label.name

            # Hierarchical label is not supported in Kylin
            # quote label as a temp hack
            if labelname.find('.') >= 0:
                labelname = '"%s"' % labelname

        if render_label_with_as:
            if add_to_result_map is not None:
                add_to_result_map(
                    labelname,
                    label.name,
                    (label, labelname, ) + label._alt_names,
                    label.type
                )

            return label.element._compiler_dispatch(
                self, within_columns_clause=True,
                within_label_clause=True, **kw) + \
                   OPERATORS[operators.as_] + \
                   self.preparer.format_label(label, labelname)
        elif render_label_only:
            return self.preparer.format_label(label, labelname)
        else:
            return label.element._compiler_dispatch(
                self, within_columns_clause=False, **kw)

    def visit_column(self, column, add_to_result_map=None,
                     include_table=True, **kwargs):
        name = orig_name = column.name
        if name is None:
            raise exc.CompileError("Cannot compile Column object until "
                                   "its 'name' is assigned.")

        is_literal = column.is_literal
        if not is_literal and isinstance(name, elements._truncated_label):
            name = self._truncated_identifier("colident", name)

        if add_to_result_map is not None:
            add_to_result_map(
                name,
                orig_name,
                (column, name, column.key),
                column.type
            )

        if is_literal:
            name = self.escape_literal_column(name)
        elif name.find('.') >= 0:
            # Hierarchical label is not supported in Kylin
            # quote label as a temp hack
            name = '"%s"' % name
            name = self.preparer.quote(name)
        else:
            name = self.preparer.quote(name)

        table = column.table
        if table is None or not include_table or not table.named_with_column:
            return name
        else:
            if table.schema:
                schema_prefix = self.preparer.quote_schema(table.schema) + '.'
            else:
                schema_prefix = ''
            tablename = table.name
            if isinstance(tablename, elements._truncated_label):
                tablename = self._truncated_identifier("alias", tablename)

            return schema_prefix + \
                   self.preparer.quote(tablename) + \
                   "." + name


class KylinIdentifierPreparer(IdentifierPreparer):
    # Kylin is case sensitive, temp hack to turn off name quoting
    def __init__(self, dialect, initial_quote='',
                 final_quote=None, escape_quote='', omit_schema=False):
        super(KylinIdentifierPreparer, self).__init__(dialect, initial_quote, final_quote, escape_quote, omit_schema)


class KylinDialect(default.DefaultDialect):
    name = 'kylin'
    driver = 'pykylin'

    preparer = KylinIdentifierPreparer
    preexecute_pk_sequences = True
    supports_pk_autoincrement = True
    supports_sequences = True
    sequences_optional = True
    supports_native_decimal = True
    supports_default_values = True
    supports_native_boolean = True
    poolclass = pool.SingletonThreadPool
    supports_unicode_statements = True

    default_paramstyle = 'pyformat'

    def __init__(self, **kwargs):
        super(KylinDialect, self).__init__(self, **kwargs)

    @classmethod
    def dbapi(cls):
        return __import__('pykylin')

    def initialize(self, connection):
        self.server_version_info = None
        self.default_schema_name = None
        self.default_isolation_level = None
        self.returns_unicode_strings = True

    def create_connect_args(self, url):
        opts = url.translate_connect_args()
        args = {
            'username': opts['username'],
            'password': opts['password'],
            'endpoint': 'http://%s:%s/%s' % (opts['host'], opts['port'], opts['database'])
        }
        args.update(url.query)
        return [], args

    def get_table_names(self, connection, schema=None, **kw):
        return connection.connection.list_tables()

    def has_table(self, connection, table_name, schema=None):
        return table_name in self.get_table_names(connection, table_name, schema)

    def has_sequence(self, connection, sequence_name, schema=None):
        return False

    def get_columns(self, connection, table_name, schema=None, **kw):
        cols = connection.connection.list_columns(table_name)
        return [self._map_column_type(c) for c in cols]

    def _map_column_type(self, column):
        tpe_NAME = column['type_NAME']
        if tpe_NAME.startswith('VARCHAR'):
            tpe_size = column['column_SIZE']
            args = (tpe_size,)
            tpe = KYLIN_TYPE_MAP['VARCHAR']
        elif tpe_NAME == 'DECIMAL':
            digit_size = column['decimal_DIGITS']
            args = (digit_size,)
            tpe = KYLIN_TYPE_MAP['DECIMAL']
        else:
            args = ()
            tpe = KYLIN_TYPE_MAP[tpe_NAME]
        column_tpe = tpe(*args)
        return {
            'name': column['column_NAME'].lower(),
            'type': column_tpe
        }

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        return []

    def get_indexes(self, connection, table_name, schema=None, **kw):
        return []

    def get_view_names(self, connection, schema=None, **kw):
        return []

    def get_pk_constraint(self, conn, table_name, schema=None, **kw):
        return {}

    def get_unique_constraints(
            self, connection, table_name, schema=None, **kw):
        return []

