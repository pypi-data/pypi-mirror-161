"""
All sources of readable data are described by SqlDataSupplier.  It's getTableStream() method lets you get an
accessor for a table, which is returned as an instance of SqlTableStream.
"""
import functools

from .misc import loose_table_match


class SqlDataSupplier(object):
    """
    A source of data, i.e. tables.
    """
    def getTableStream(self, table_spec: tuple[str]):
        """
        Returns a SqlTableStream for a given table specification, which is a tuple ending in a table name
        and optionally preceded by a database name.
        """


class SqlTableStream(object):
    """
    An iterable set of rows, plus descriptions of the returned fields.
    """
    def __init__(self, upstream=None):
        self.upstream = upstream
        self.context = None

    def supplyContext(self, context):
        """
        Before a compiled object can operate it may need some context.

        :param context:  An instance of SqlEvaluationContext.
        """
        if self.upstream:
            if isinstance(self.upstream, (tuple, list)):
                for s in self.upstream:
                    s.supplyContext(context)
            else:
                self.upstream.supplyContext(context)
        self.context = context

    def getFields(self):
        """
        Return the list of SqlFieldInfo for each field this stream returns.
        """
        if self.upstream:
            return self.upstream.getFields()
        return []

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        """
        Return an iterable sequence of rows.  Each row is a tuple containing values for each field listed
        by getFields().
        """
        if self.upstream:
            return self.upstream.getRowIterator(where, sort, start, count)
        return []

    def asDataFrame(self, where=None):
        """
        Convert a TableStream into a pandas DataFrame.
        """
        import pandas
        cols = list(map(lambda f:f.field,self.getFields()))
        cols_out = {col: [] for col in cols}
        for row_data in self.getRowIterator(where):
            for n_col, col in enumerate(cols):
                cols_out[col].append(row_data[n_col])
        return pandas.DataFrame(data=cols_out)

    def canSort(self, sort):
        """
        Implementations can declare whether they support sorting, with a given sort specification.
        """
        if self.upstream:
            return self.upstream.canSort(sort)
        return True

    def canWhere(self, where):
        """
        Implementations can declare whether they can handle a given WHERE clause.
        """
        if self.upstream:
            return self.upstream.canWhere(where)
        return True

    def canLimit(self, start, count):
        """
        Declares whether this implementation can handle the supplied start/count (limit) values.
        """
        if self.upstream:
            return self.upstream.canLimit(start, count)
        return True


class SqlFieldInfo(object):
    """
    Metadata about a single field.
    """
    def __init__(self, table=None, field=None, database=None, alias=None, table_alias=None):
        self.database = database
        self.table = table
        self.table_alias = table_alias
        self.field = field
        self.alias = alias

    def __str__(self):
        out = ""
        if self.database:
            out += self.database + "."
        if self.table:
            out += self.table
        if self.table_alias:
            out += "(" + self.table_alias + ")"
        out += "."
        if self.field:
            out += self.field
        if self.alias:
            out += "(" + self.alias + ")"
        return out


class MemoryDataSupplier(SqlDataSupplier):
    """
    Provides table data from data in memory.
    """
    def __init__(self, data, db_name=None, allow_sort: bool=True):
        self.data = data
        self.dbName = db_name
        self._allow_sort = allow_sort

    def getTableStream(self, table_spec):
        table_name = table_spec[-1]
        db_name = table_spec[-2] if len(table_spec) > 1 else None
        if self.dbName or db_name:
            if not self.dbName or not db_name:
                return None
            if db_name.lower() != self.dbName.lower():
                return None
        real_table_name = loose_table_match(table_name, self.data)
        if not real_table_name:
            return None
        col_names = set()
        rows = self.data[real_table_name]
        for row in rows:
            for col in row.keys():
                col_names.add(col)
        col_names = sorted(list(col_names))
        return MemStream(real_table_name, rows, col_names, table_name=table_name, allow_sort=self._allow_sort)


class MemStream(SqlTableStream):
    def __init__(self, name, rows, col_names, table_name, allow_sort):
        super(MemStream, self).__init__()
        self.rows = rows
        self.fields = [SqlFieldInfo(name, field) for field in col_names]
        self.table_name = table_name
        self._allow_sort = allow_sort

    def supplyContext(self, context):
        self.context = context.derive(fields=self.getFields())

    def getFields(self):
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        rows = (tuple([row.get(field.field) for field in self.fields]) for row in self.rows)
        if sort:
            def sort_cmp(a, b):
                return sort.compare(a, b, self.context)
            rows = sorted(rows, key=functools.cmp_to_key(sort_cmp))
        if start or count >= 0:
            rows = list(rows)
            if count >= 0:
                rows = rows[start:start+count]
            else:
                rows = rows[start:]
        for row in rows:
            if self.context and self.context.debugLevel:
                print("MemoryDataSupplier: t={0}, row:{1}".format(self.table_name, row))
            yield row

    def canLimit(self, start, count):
        return True

    def canWhere(self, where):
        return not where

    def canSort(self, sort):
        return not sort or self._allow_sort
