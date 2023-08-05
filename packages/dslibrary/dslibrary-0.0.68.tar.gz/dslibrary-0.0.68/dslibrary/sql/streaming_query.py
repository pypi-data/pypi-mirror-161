import dslibrary

from .compiler import SqlCompiler
from .eval_utils import SqlEvaluationContext
from .misc import table_name_from_table_spec, format_options_for_table
from .parser import SqlParser
from .data import SqlTableStream, SqlFieldInfo, SqlDataSupplier


def open_row_stream(resource_name, chunksize_bytes=10000000, table_format_options=None, **kwargs):
    """
    Generate a streaming row iterator that returns one row's data at a time.  The iterator
    will have a 'columns' property with column names.
    :param resource_name:   A filename or a file-like object, or the name of any resource that dslibrary is able to
        open.  A ChunkedRowIterator() can also be returned, to reference arbitrary external data.
    :param chunksize_bytes: Desired bytes per chunk for streaming.
    :param table_format_options: DataFileMetrics formatting overrides.
    :param kwargs:          Additional arguments to send to dslibrary.load_dataframe().
    :return:                A streaming row iterator.
    """
    if isinstance(resource_name, ChunkedRowIterator):
        return resource_name
    format_options = dict(table_format_options or {})
    format_options["chunksize_bytes"] = chunksize_bytes
    reader = dslibrary.load_dataframe(resource_name, format_options=format_options, **kwargs)
    rows = ChunkedRowIterator(reader)
    if hasattr(resource_name, "read"):
        rows.on_close.append(resource_name.close)
    return rows


def streaming_query(sql: str, stream_opener, chunksize_bytes=10000000, format_options=None):
    """
    Run SQL against streaming file-like data sources.  Only CSV is supported at the moment.
    :param sql:             SQL to run
    :param stream_opener:   Opens a file-like object given the name of a table.
    :param chunksize_bytes:      Approximate bytes per chunk.
    :param format_options:  A mapping from table name to a {} with DataFileMetrics format options.  Use a blank
                            key for default format options.
    :return:                A tuple with 0) column names, and 1) a row iterator for row values.
    """
    def opener(table_spec):
        table_name = table_name_from_table_spec(table_spec)
        clean_spec = (table_name,) if isinstance(table_spec, str) else table_spec[:-1] + (table_name,)
        base_stream = stream_opener(clean_spec)
        tbl_opts = format_options_for_table(format_options, table_spec)
        return open_row_stream(base_stream, chunksize_bytes=chunksize_bytes, table_format_options=tbl_opts)
    data = GenericDataSupplier(opener=opener)
    c = SqlCompiler()
    sel = SqlParser(sql).parse_select_only()
    ctx = SqlEvaluationContext(compiler=c)
    ctx.addDataSupplier(data)
    compiled = c.compile_select(sel, ctx)
    compiled.supplyContext(ctx)
    cols = tuple(field.alias or field.field for field in compiled.getFields())
    rows = compiled.getRowIterator()
    return cols, rows


class ChunkedRowIterator(object):
    """
    Turn a pandas TextFileReader instance into a row iterator.  Each iteration yields a tuple of column values for one
    row.  The 'columns' field indicates the names of each column.
    """
    def __init__(self, reader, cols=None, rows=None, closer=None):
        """
        Supply either 'reader', i.e. the result of pandas.load_csv() with a chunk_size specified, or 'cols' and 'rows'.

        :param reader:      An object with a get_chunks() and a close() method, or None.
        :param cols:        Column names.
        :param rows:        An iterable list of tuples for each row.
        :param closer:      Method to call when iteration ends.
        """
        self.reader = reader
        self.columns = cols
        self.row_gen = rows
        self.dtypes = None
        self.on_close = []
        if closer:
            self.on_close.append(closer)
        if self.row_gen is None:
            self._next_chunk()

    def _next_chunk(self):
        df = self.reader.get_chunk()
        if not self.columns:
            self.columns = list(df.columns)
            self.dtypes = list(df.dtypes)
        self.chunk_len = df.shape[0]
        self.chunk_iter = df.itertuples(index=False, name=None)

    def __iter__(self):
        if self.row_gen:
            return iter(self.row_gen)
        return self

    def __next__(self):
        while True:
            try:
                return next(self.chunk_iter)
            except StopIteration:
                self._next_chunk()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.reader is not None:
            self.reader.close()
        self.reader = None
        for handler in self.on_close:
            handler()
        self.on_close.clear()


class RowIteratorTableStream(SqlTableStream):
    """
    An adapter for ChunkedRowIterator to plug it into the SQL interpreter.
    """
    def __init__(self, table_name, open_stream):
        super(SqlTableStream, self).__init__()
        self.open_stream = open_stream
        self.table_name = table_name
        stream = open_stream()
        self.fields = [SqlFieldInfo(table_name, field) for field in stream.columns]
        stream.close()

    def supplyContext(self, context):
        self.context = context.derive(fields=self.getFields())

    def getFields(self):
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        # TODO support where and other features here: pandas is faster than we are at this
        stream = self.open_stream()
        for row in iter(stream):
            yield row
        stream.close()

    def canLimit(self, start, count):
        if start or count >= 0:
            return False
        return True

    def canWhere(self, where):
        return not where

    def canSort(self, sort):
        if not sort:
            return True
        return False


class GenericDataSupplier(SqlDataSupplier):
    """
    Adapter for the SQL interpreter that supports streaming of large files.  See streaming_query().
    """
    def __init__(self, opener, db_name: str = None):
        self.opener = opener
        self.db_name = db_name

    def getTableStream(self, table_spec):
        table_name = table_spec[-1]
        db_name = table_spec[-2] if len(table_spec) > 1 else None
        if self.db_name or db_name:
            if not self.db_name or not db_name:
                return None
            if db_name.lower() != self.db_name.lower():
                return None
        return RowIteratorTableStream(table_name, lambda: self.opener(table_name))
