"""
Modifications to SQL.
"""
import re

from .parser import SqlParser
from .select_stmt import SqlSelect
from .compiled import Node_Literal, Node_Field, Node
from .tokenize import SqlTokenizer, Token
from .misc import enquote_string_literal, sql_enquote_id
from .eval_utils import OPS_ALL


def impose_sql_limit(sql: str, limit: int=None, flavor: str=None):
    """
    Inject a limit on some SQL.  Also reformats to the selected flavor/dialect.
    :param sql:  SQL to modify.  Must be a SELECT statement.
    :param limit: Limit to insert.
    :param flavor:  Language variant (see sql_enquote_id()).
    """
    select = SqlParser(sql, allow_any_function=True).parse_select()
    if not select:
        # not a SELECT statement
        return sql

    def apply(sel):
        use_lim = limit
        if sel.limit:
            use_lim = min(limit, sel.limit.eval(None))
        sel.limit = Node_Literal(use_lim)

    if limit:
        if select.union:
            # limit is applied to last union
            apply(select.union[-1])
        else:
            apply(select)
    return select.to_sql(flavor)


def limit_sql_cursor_rows(base_cursor, max_rows: int=None):
    """
    Prevent a DBI cursor from returning more than a given number of rows.

    :param base_cursor:  A DBI cursor, or a jdbc.Runner() instance, which wraps such a connection/cursor.
    """
    class MaxRowsCursor(object):
        def __init__(self):
            self.description = self._descr()
            self._remaining = None if max_rows is None else max(max_rows, 0)

        def _cursor(self):
            if hasattr(base_cursor, "cursor"):
                return base_cursor.cursor
            return base_cursor

        def _descr(self):
            c = self._cursor()
            if c is not None and hasattr(c, "description"):
                return c.description

        def _available(self, n: int):
            if self._remaining is None:
                return n
            if n >= self._remaining:
                return self._remaining
            return n

        def _use(self, n: int):
            if self._remaining is None:
                return
            self._remaining -= n
            if self._remaining == 0:
                self.close()

        def start(self):
            r = None
            if hasattr(base_cursor, "start"):
                r = base_cursor.start()
                if not self.description:
                    self.description = self._descr()
            return r

        def stop(self):
            self.close()

        def close(self):
            if hasattr(base_cursor, "stop"):
                base_cursor.stop()
            elif hasattr(base_cursor, "close"):
                base_cursor.close()
            self._remaining = 0

        def fetchone(self):
            n = self._available(1)
            if n:
                r = self._cursor().fetchone()
                if not r:
                    self.close()
                    self._remaining = 0
                self._use(n)
                return r

        def fetchall(self):
            if self._remaining is None:
                return self._cursor().fetchall()
            use = self._remaining
            r = self._cursor().fetchmany(use)
            self._use(use)
            return r

        def fetchmany(self, n: int):
            if self._remaining is None:
                return self._cursor().fetchmany(n)
            use = self._available(n)
            r = self._cursor().fetchmany(use)
            self._use(use)
            return r

        def __next__(self):
            r = self.fetchone()
            if not r:
                raise StopIteration
            return r

        def __iter__(self):
            return self

    return MaxRowsCursor()


def looks_like_sql(sql: str):
    """
    Differentiate between SQL and other strings.
    """
    if not sql:
        return False
    # any sql comment implies sql
    if "/*" in sql and "*/" in sql:
        return True
    # sql verbs
    if re.match(r'^\s*(with|select|insert|create|describe)\s+[^\s].*', sql, re.IGNORECASE | re.DOTALL):
        return True
    return False


def just_a_table_name(sql: str, interpret_select: bool=True):
    """
    Detect a string which is just a table name, i.e. "table", or SQL that only references a table with no modification,
    i.e. "select * from table".
    """
    if not sql or not isinstance(sql, str):
        return
    if looks_like_sql(sql):
        if not interpret_select:
            return
        m = re.match(r'^(?:\s+|/\*.*?\*/)*select\s+\*\s+from\s("[^\n]*?"|`[^\n]*?`|[^\s]+)\s*$', sql, re.DOTALL | re.I)
        if m:
            name = m.group(1)
            if len(name) >= 2 and name[0] in ('"', "`") and name[0] == name[-1]:
                name = name[1:-1]
            return name
        return
    # some strings are not likely to be table names
    if "\n" in sql or len(sql) > 255:
        return
    return sql


def _rebuild_from_tokens(sql, draw_placeholder):
    tokens = SqlTokenizer(sql, OPS_ALL, allow_placeholders=True).run()
    bits = []
    pos = 0
    n_param = 0
    for token in tokens:
        if token.type != Token.PLACEHOLDER:
            continue
        if token.pos > pos:
            bits.append(sql[pos:token.pos])
        s_token = draw_placeholder(token, n_param) or "NULL"
        bits.append(s_token)
        n_param += 1
        pos = token.pos + token.len
    bits.append(sql[pos:])
    return "".join(bits)


def embed_parameters(sql: str, parameters: (list, tuple)):
    """
    Replace placeholders in SQL with a given set of parameters.
    :param sql:                 SQL with placeholders '%s' or '?'.
    :param parameters:          An iteration of values.
    :return:        Filled-out SQL.
    """
    def draw_placeholder(token, n_param):
        if parameters and n_param < len(parameters):
            v = parameters[n_param]
            if isinstance(v, str):
                return enquote_string_literal(v)
            else:
                return str(v)
    return _rebuild_from_tokens(sql, draw_placeholder)


def reformat_placeholders(sql: str, flavor: str=None):
    """
    Reformat placeholders in SQL to match the target database engine.
    """
    if "?" not in sql and "%s" not in sql:
        return sql
    flavor_ph = "%s"
    def draw_placeholder(token, n_param):
        return flavor_ph
    return _rebuild_from_tokens(sql, draw_placeholder)


def apply_default_table_name(sql: str, use_table: str, default_table_names: tuple=("table",), flavor: str=None):
    """
    SQL can be written using a default table name, and then that default table can be replaced with an actual table
    name.
    """
    # no table supplied: return unchanged SQL
    if not use_table:
        return sql
    # table name only?  Return the supplied table name instead.
    tn_only = just_a_table_name(sql)
    if tn_only:
        if tn_only in default_table_names:
            if looks_like_sql(sql):
                return "select * from " + sql_enquote_id(use_table, mode=flavor)
            return use_table
        return sql
    sel = SqlParser(sql, allow_any_function=True).parse_select()
    def replacer(table_spec):
        if len(table_spec) == 1 and table_spec[-1] in default_table_names:
            return (use_table,)
        return table_spec
    sel.map_tables(replacer)
    return sel.to_sql(flavor)


class BuildSqlSelect(object):
    def __init__(self, sql: str=None):
        """
        Begin building a SELECT, optionally starting from the given SQL.
        """
        if sql:
            self.statement = SqlParser(sql).parse_select_only()
        else:
            self.statement = SqlSelect()

    def distinct(self):
        """
        Add the 'distinct' clause.
        """
        self.statement.distinct = []
        return self

    def field(self, expr, alias: str = None):
        """
        Add a field to return from the SELECT.
        """
        if self.statement.fields is None:
            self.statement.fields = []
        if isinstance(expr, str):
            self.statement.fields.append((Node_Field((expr,)), alias))
        elif isinstance(expr, (tuple, list)):
            self.statement.fields.append((Node_Field(tuple(part) for part in expr), alias))
        elif isinstance(expr, Node):
            self.statement.fields.append((expr, alias))
        else:
            raise Exception(f"misuse of field(), expr={expr}")
        return self

    def set_from(self, expr, alias: str=None):
        """
        Set the source table.
        """
        if isinstance(expr, str):
            self.statement.from_expr = SqlSelect.FromExpr()
            self.statement.from_expr.table = (expr,)
        elif isinstance(expr, (tuple, list)):
            self.statement.from_expr = SqlSelect.FromExpr()
            self.statement.from_expr.table = tuple(expr)
        else:
            raise Exception(f"misuse of set_from(), expr={expr}")
        self.statement.from_expr.alias = alias
        return self

    def where(self, expr):
        """
        Specify WHERE clause.
        """
        if isinstance(expr, str):
            self.statement.where = SqlParser(expr).parse_expr()
        elif isinstance(expr, Node):
            self.statement.where = expr
        else:
            raise Exception(f"misuse of where(), expr={expr}")
        return self

    def limit(self, expr):
        """
        Specify a limit.
        """
        if isinstance(expr, int):
            self.statement.limit = Node_Literal(expr)
        elif isinstance(expr, Node):
            self.statement.limit = expr
        else:
            raise Exception(f"misuse of limit(), expr={expr}")
        return self


