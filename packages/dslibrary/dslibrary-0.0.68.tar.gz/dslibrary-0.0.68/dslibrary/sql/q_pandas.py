import pandas

from .compiler import SqlCompiler
from .data import SqlFieldInfo, SqlDataSupplier, SqlTableStream
from .eval_utils import SqlEvaluationContext
from .misc import loose_table_match
from .modify_sql import embed_parameters
from .parser import SqlParser
from .. import DSLibraryException
from ..utils.df_utils import coerce_to_dataframe


def accessor_for_tables(tables, table_lookup: callable=None, table_loader: callable=None, fallback_data=None):
    """
    Generate a data supplier that will read from a collection of named pandas dataframes.
    :param tables:  A {} mapping table names to pandas.DataFrame.
    :param table_lookup:  A function to look up a real table name from a supplied table name tuple.  The default uses
                          loose_table_match() on the last table name element.
    :param table_loader:  A function that looks up a table name tuple and returns a DataFrame.
    :param fallback_data:  If no table is matched, this data is queried.
    """
    if tables is None:
        tables = {}

    class Stream(SqlTableStream):
        def __init__(self, name, use_name):
            super(Stream, self).__init__()
            self.name = name if isinstance(name, str) else name[-1]
            if table_loader:
                data = table_loader(name)
            else:
                data = tables.get(self.name)
            if data is None:
                data = fallback_data
            self.dataframe = coerce_to_dataframe(data)
            self.fields = [SqlFieldInfo(use_name, field) for field in self.dataframe]

        def supplyContext(self, context):
            self.context = context.derive(fields=self.getFields())

        def getFields(self):
            return self.fields

        def getRowIterator(self, where=None, sort=None, start=0, count=-1):
            df = self.dataframe
            if count != -1:
                df = df.iloc()[start:start + count]
            elif start:
                df = df.iloc()[start:]
            for row in df.itertuples(index=False):
                yield row

        def canLimit(self, start, count):
            return True

        def canWhere(self, where):
            # TODO support this by compiling 'where' into a pandas filter
            if where:
                return False
            return True

        def canSort(self, sort):
            # TODO support this using sort_values()
            if sort:
                return False
            return True

    class Accessor(SqlDataSupplier):
        def getTableStream(self, table_spec):
            if table_loader:
                return Stream(table_spec, table_spec[-1])
            if table_lookup:
                table_name = table_lookup(table_spec)
            else:
                table_name = loose_table_match(table_spec[-1], tables)
            if table_name in tables or fallback_data is not None:
                return Stream(table_name or table_spec[-1], table_spec[-1])

    return Accessor()


def sql_for_data_suppliers(sql, data_suppliers, ext_vars: dict=None, sql_parameters: list=None):
    """
    Run SQL against a set of DataSupplier instances, returning a DataFrame.

    :param sql:                 SQL to run.
    :param data_suppliers:      Sources of data (i.e. 'all the tables').
    :param ext_vars:            Variables referenced by the SQL.
    :param sql_parameters:      Parameters to inject into SQL that references them, i.e. with '?'.

    :return:        A DataFrame.
    """
    if sql_parameters:
        sql = embed_parameters(sql, sql_parameters)
    context = SqlEvaluationContext(data_suppliers=data_suppliers, ext_vars=ext_vars)
    select = SqlParser(sql).parse_select()
    stream = SqlCompiler().compile_select(select, context)
    columns = tuple(f.field for f in stream.getFields())
    return pandas.DataFrame(data=stream.getRowIterator(), columns=columns)


def sql_for_tables(sql, tables: dict=None, ext_vars: dict=None, table_loader=None, fallback_data=None, sql_parameters: list=None):
    """
    Run SQL against a set of tables.

    :param tables:          A {} mapping table names to dataframes.
    :param sql:             SQL to run.
    :param ext_vars:        External variables referenced by the SQL.
    :param table_loader:    A function that will return a DataFrame given a table name.
    :param fallback_data:   DataFrame to use in case a table is not matched.
    :param sql_parameters:      Parameters to inject into SQL that references them, i.e. with '?'.

    :return:    A DataFrame.
    """
    if bool(tables) + bool(table_loader) + bool(fallback_data is not None) < 1:
        raise DSLibraryException("Specify at least one of 'tables', 'table_loader' or 'fallback_data'")
    if bool(tables) + bool(table_loader) > 1:
        raise DSLibraryException("Specify at most one of 'tables' and 'table_loader'")
    if sql_parameters:
        sql = embed_parameters(sql, sql_parameters)
    src = accessor_for_tables(tables, table_loader=table_loader, fallback_data=fallback_data)
    return sql_for_data_suppliers(sql, [src], ext_vars=ext_vars)
