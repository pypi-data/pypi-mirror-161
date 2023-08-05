"""
Remote, chunkable database connection: implements the standard Python API for a database connection,
calling remote services to read and write data.

Db interface specification: https://www.python.org/dev/peps/pep-0249/
"""
import time
import datetime
import re

from dslibrary.sql.misc import sql_split

apilevel = "1.0"
threadsafety = 2   # 1=module is thread-safe, 2=connections are thread-safe, 3=cursors are thread-safe
paramstyle = "format"  # expects '%s' for parameter replacements

Binary = bytes
Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
DateFromTicks = lambda ticks: Date(*time.localtime(ticks)[:3])
TimeFromTicks = lambda ticks: Time(*time.localtime(ticks)[3:6])
TimestampFromTicks = lambda ticks: Timestamp(*time.localtime(ticks)[:6])


class _DBAPITypeObject:
    def __init__(self, *values):
        self.values = values
    def __eq__(self, other):
        if other in self.values:
            return True
        else:
            return False
    def __ne__(self, other):
        if other in self.values:
            return False
        else:
            return True

STRING = _DBAPITypeObject(str)
BINARY = _DBAPITypeObject(bytes)
NUMBER = _DBAPITypeObject(int, float, bool)
DATETIME = _DBAPITypeObject(datetime.datetime, datetime.date, datetime.time)
ROWID = _DBAPITypeObject()

class Error(Exception): pass
class Warning(Exception): pass
class InterfaceError(Error): pass
class DatabaseError(Error): pass
class InternalError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class DataError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass


class Connection(object):
    def __init__(self, read: callable, write: callable=None, read_more: callable=None, flavor: str=None):
        """
        Create a DBI-compatible adapter that uses the supplied functions.
        :param read:        A method with two arguments: sql and parameters.  Returns cols, rows, more.  Cols will be
            returned for cursor 'description'.  Row is a list of row values.  More should be None if there are no more
            rows, or else a hint to read_more() for the next page.
        :param write:       A method with two arguments: sql and parameters.
        :param read_more:   A method with one argument: 'more'.  Returns cols, rows, more, (same as read()).
        :param flavor:      Type of database being emulated/proxied.  'mysql', 'postgres', 'bigquery', etc. - see also
                            db_conn_flavor().
        """
        self.read = read
        self.read_more = read_more
        self.write = write
        self._flavor = flavor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """ clean up """

    def commit(self):
        """ commit changes (placeholder) """

    def rollback(self):
        """ roll back changes (placeholder) """

    def cursor(self):
        return Cursor(self)


class Cursor(object):
    def __init__(self, conn: Connection):
        self._conn = conn
        self._cols = []
        self._rows = []
        self._pos = 0
        self.arraysize = 0
        self._ops = []

    @property
    def description(self):
        return self._cols

    @property
    def rowcount(self):
        return len(self._rows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def callproc(self, procname, *parameters):
        raise NotSupportedError()

    def close(self):
        self._cols = []
        self._rows = []
        self._more = None
        self._ops = []
        self._pos = 0

    def execute(self, operation, parameters=None):
        self.close()
        tbl_only = _is_table_name(operation)
        if tbl_only:
            operation = 'select * from "%s"' % operation
        if _is_read_operation(operation):
            self._ops = list(sql_split(operation, parameters))
            self.nextset()
            return self
        else:
            if not self._conn.write:
                raise OperationalError("no write access")
            self._conn.write(operation, parameters)

    def nextset(self):
        if self._ops:
            op, op_params = self._ops.pop(0)
            self._cols, self._rows, self._more = self._conn.read(op, op_params)
            self._pos = 0
        else:
            raise OperationalError()

    def _ensure_next(self, n):
        # throw out rows as we go, but not too often to avoid wasting memory
        if self._pos > 1000:
            self._rows = self._rows[self._pos:]
            self._pos = 0
        # no 'read_more' function?
        if not self._conn.read_more:
            return
        # read more chunks
        while self._more:
            avail = len(self._rows) - self._pos
            if avail >= n:
                return
            more_rows, self._more = self._conn.read_more(self._more)
            self._rows += more_rows

    def fetchone(self):
        self._ensure_next(1)
        if self._pos < len(self._rows):
            p = self._pos
            self._pos += 1
            return self._rows[p]

    def fetchmany(self, size):
        self._ensure_next(size)
        avail = len(self._rows) - self._pos
        if size > avail:
            size = avail
        p = self._pos
        self._pos += size
        return self._rows[p: self._pos]

    def fetchall(self):
        self._ensure_next(1000000000000)
        p = self._pos
        self._pos = len(self._rows)
        return self._rows[p:]

    def executemany(self, operation, seq_of_parameters):
        if _is_read_operation(operation):
            raise OperationalError()
        else:
            for params in seq_of_parameters:
                self.execute(operation, params)

    def setinputsizes(self, sizes):
        """ placeholder """

    def setoutputsize(self, size, column=None):
        """ placeholder """

    def __next__(self):
        row = self.fetchone()
        if row:
            return row
        raise StopIteration

    def __iter__(self):
        return self


def _is_read_operation(operation):
    """
    Detect a read-only SQL operation.
    """
    verb = re.split(r'\s+', operation[:20].lower().strip())[0]
    return verb in {"select", "show", "describe"}


def _is_table_name(operation):
    """
    Detect "just a table name".  Returns the table name or None.
    """
    operation = operation.strip()
    m = re.match(r'^(([A-Za-z_][A-Za-z_0-9\-]*)|`([^`]+)`|"([^`]+)"|\[([^]]+)])$', operation)
    if m is None:
        return
    return m.group(2) or m.group(3) or m.group(4) or m.group(5)
