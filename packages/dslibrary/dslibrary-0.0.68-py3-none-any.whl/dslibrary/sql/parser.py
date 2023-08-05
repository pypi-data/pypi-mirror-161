"""
Parsing of SQL.
"""
from collections import OrderedDict

from .compiled import Node_Placeholder, Node_Literal, Node_Unary, Node_Field, Node_ExtVar, ALL_FUNCTIONS, \
    Node_Select, Node_Cast, Node_InSelect, Node_Op, Node_Op_Is, Node_List, Node_Function, Node_Case, SqlOrderBy, \
    AGGREGATE_FNS
from .exceptions import SqlException
from .tokenize import SqlTokenizer, Token
from .eval_utils import OPS_ALL, OP_PRECEDENCE, UOPS
from .select_stmt import SqlSelect


class SqlParser(object):
    """
    Parsing of SQL statements.

    Grammar/functions are similar to SQLite3.
    """
    # function names
    FN_ALL = ALL_FUNCTIONS | AGGREGATE_FNS

    def __init__(self, sql: str, allow_any_function: bool=False):
        self.input = sql
        self.tokens = self.tokenize(sql)
        self.pos = 0
        self.tables = []
        self.views = []
        self.table_map = {}
        self.view_map = {}
        self.view_filter = None
        self.allow_any_function = allow_any_function
        self.compiled_class = SqlSelect
        self.FROM_RESERVED_KEYWORDS = FROM_RESERVED_KEYWORDS[:]

    def tokenize(self, input: str):
        return SqlTokenizer(input, allowed_operators=OPS_ALL, allow_placeholders=True).run()

    def report_error(self, message):
        token = self.cur_token()
        pos = token.pos if token is not None else len(self.input)
        tkn_value = token.value if token is not None else "<end>"
        # find line and column
        lines = self.input[0:pos].split("\n")
        line = len(lines)
        col = len(lines[-1]) + 1
        b = pos - 40
        if b < 0:
            b = 0
        e = pos + 40
        if e > len(self.input):
            e = len(self.input)
        context = '"' + ("..." if b > 0 else "") + self.input[b:pos] + "<*>" + self.input[pos:e] + (
            "..." if e < len(self.input) else "") + '"'
        raise SqlParserException(message, line=line, col=col, token=tkn_value, context=context)

    def cur_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next_token(self):
        if self.pos + 1 > len(self.tokens):
            return None
        self.pos += 1
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def peek_token(self, offset):
        if self.pos + offset < 0 or self.pos + offset >= len(self.tokens):
            return None
        return self.tokens[self.pos + offset]

    def _peek_test(self, offset, cmp_value):
        token = self.peek_token(offset)
        if not token:
            return False
        if cmp_value == str(token.value).lower():
            return True
        return False

    def skip_punct(self, p, error_if_missing=False):
        t = self.cur_token()
        if t and t.isPunct(p):
            self.next_token()
            return True
        if error_if_missing:
            self.report_error("Expected '" + p + "'")
        return False

    def any_keyword(self, what_its_for=None, ret_token=False):
        t = self.cur_token()
        if not t or t.type != Token.KEYWORD:
            self.report_error("Expected " + (what_its_for or "keyword"))
        self.next_token()
        return t if ret_token else t.value

    def test_keyword(self, kwd):
        """
        Check whether a particular keyword is present at the current position.
        """
        return self.skip_keyword(kwd, skip=False)

    def skip_keyword(self, kwd, skip=True):
        """
        Check whether a given keyword (or a list of keywords) is present
        at the current position.  They are skipped if they are detected and if the
        'skip' argument is not set to False.
        """
        # check for compound keyword
        if isinstance(kwd, list):
            for n in range(0, len(kwd)):
                t = self.peek_token(n)
                if not t or not t.isKeyword(kwd[n]):
                    return False
            if skip:
                self.pos += len(kwd)
            return True
        # single keyword
        t = self.cur_token()
        if t and t.isKeyword(kwd):
            if skip:
                self.next_token()
            return True
        return False

    def parse_field_name(self):
        tkn = self.any_keyword("field name", ret_token=True)
        field_name = [tkn.value]
        quotes = [bool(tkn.etc)]
        while self.skip_punct('.'):
            next_field = self.any_keyword("field component", ret_token=True)
            field_name.append(next_field.value)
            quotes.append(bool(next_field.etc))
        return tuple(field_name), tuple(quotes)

    def parse_table_name(self):
        table_name = [self.any_keyword("table name")]
        while self.skip_punct('.'):
            next_part = self.any_keyword("table component")
            table_name.append(next_part)
        return tuple(table_name)

    def parse_value(self):
        """
        <value> :=
          <number>
          <string>
          NULL
          - <value>
          '(' <expr> ')'
          <name (field)>
          <name> '(' ... ')'
        """
        t = self.cur_token()
        if not t:
            return None
        if t.isLiteral():
            self.next_token()
            if t.type == Token.PLACEHOLDER:
                return Node_Placeholder()
            return Node_Literal(value=t.value)
        elif t.value in UOPS:
            self.next_token()
            return Node_Unary(child=self.parse_value(), operator=t.value)
        elif self.skip_keyword("null"):
            return Node_Literal(value=None)
        elif self.skip_punct('('):
            return self.parse_parens()
        elif self.skip_keyword("case"):
            return self.parse_case()
        elif self.skip_keyword("cast"):
            return self.parse_cast()
        elif self.skip_punct('*'):
            # wildcard, i.e. count(*)
            return Node_Field("*")
        elif self.skip_punct('@'):
            var_name = self.any_keyword("external variable name")
            if not var_name:
                self.report_error("expected variable name after '@'")
            return Node_ExtVar(var_name)
        elif t.type == Token.KEYWORD:
            fn_call = self.parse_function_call()
            if fn_call:
                return fn_call
            # field reference
            field_name, quotes = self.parse_field_name()
            return Node_Field(field_name, quotes)
        else:
            return None

    def parse_parens(self):
        if self.test_keyword("select"):
            sel = self.parse_select()
            if not sel:
                self.report_error("expected select statement")
            expr = Node_Select(sel)
        else:
            expr = self.parse_expr_or_list()
        self.skip_punct(')', error_if_missing=True)
        return expr

    def parse_function_call(self):
        next = self.peek_token(1)
        if next and next.isPunct('('):
            t = self.cur_token()
            # function call
            function_name = t.value.lower()
            if not self.allow_any_function and function_name not in SqlParser.FN_ALL:
                self.report_error("unrecognized function: {}".format(function_name))
            self.next_token()
            self.next_token()
            if function_name == "count" and self.skip_keyword("distinct"):
                function_name = "count_distinct"
            fn = Node_Function(function_name=function_name)
            while self.cur_token():
                v = self.parse_expr()
                if not v:
                    break
                fn.children.append(v)
                if not self.skip_punct(','):
                    break
            self.skip_punct(')')
            return fn

    def parse_cast(self):
        if not self.skip_punct('('):
            self.report_error("expected '(' after 'cast'")
        expr = self.expect_expr()
        if not self.skip_keyword("as"):
            self.report_error("expected 'as'")
        to_type = self.any_keyword("type")
        if to_type == "double" and self.skip_keyword("precision"):
            to_type += " precision"
        if to_type not in {
            "integer", "int", "tinyint", "smallint", "bigint", "double", "double precision", "float", "real", "varchar",
            "date", "datetime", "timestamp", "string"
        }:
            self.report_error("expected type")
        if self.skip_punct('('):
            length = self.parse_value()
            if not isinstance(length, Node_Literal) and not isinstance(length.value, int):
                self.report_error("expected integer length in parens")
            if not self.skip_punct(')'):
                self.report_error("expected ')'")
            to_type += "(%d)" % length.value
        if not self.skip_punct(')'):
            self.report_error("expected ')'")
        return Node_Cast(expr, to_type)

    def parse_case(self):
        parts = []
        while self.skip_keyword("when"):
            parts.append(self.expect_expr())
            if not self.skip_keyword("then"):
                self.report_error("expected 'then'")
            parts.append(self.expect_expr())
        if self.skip_keyword("else"):
            parts.append(self.expect_expr())
        if not self.skip_keyword("end"):
            self.report_error("expected 'end'")
        return Node_Case(parts)

    def parse_op(self):
        t = self.cur_token()
        if not t:
            return None
        if t.type not in [Token.PUNCT, Token.KEYWORD]:
            return None
        op = t.value.lower()
        if op not in OPS_ALL:
            return None
        self.next_token()
        return op

    def expect_expr(self):
        """
        Parse an expression and fail if none is found.
        """
        expr = self.parse_expr()
        if not expr:
            self.report_error("expected expression")
        return expr

    def parse_expr_or_list(self):
        v = self.parse_expr()
        if not v:
            return None
        if self.cur_token() and self.cur_token().value == ",":
            the_list = Node_List()
            the_list.children.append(v)
            while self.skip_punct(","):
                v = self.parse_expr()
                if not v:
                    self.report_error("expecting value after ','")
                the_list.children.append(v)
            return the_list
        return v

    def parse_expr(self):
        v_stack = []
        op_stack = []
        while True:
            v = self.parse_value()
            if not v:
                if v_stack:
                    self.report_error("expected value")
                else:
                    return v
            if self.skip_keyword("between"):
                v = self.parse_between(v)
            v_stack.append(v)
            op = self.parse_op()
            if not op:
                break
            while op_stack and OP_PRECEDENCE[op_stack[-1]] > OP_PRECEDENCE[op]:
                v_stack[-2] = self._expr_build_op(v_stack[-2], op_stack[-1], v_stack[-1])
                v_stack.pop(-1)
                op_stack.pop(-1)
            op_stack.append(op)
        while op_stack:
            v_stack[-2] = self._expr_build_op(v_stack[-2], op_stack[-1], v_stack[-1])
            v_stack.pop(-1)
            op_stack.pop(-1)
        return v_stack[0] if v_stack else None

    def parse_between(self, v_cmp):
        v_l = self.parse_value()
        if not v_l:
            self.report_error("expected value after 'between'")
        if not self.skip_keyword("and"):
            self.report_error("expected 'and' between between values")
        v_r = self.parse_value()
        if not v_r:
            self.report_error("expected value after 'between'")
        return self._expr_build_op(self._expr_build_op(v_cmp, ">=", v_l), "and", self._expr_build_op(v_cmp, "<=", v_r))

    @staticmethod
    def _expr_build_op(v_l, op, v_r):
        if op in ("in", "not in"):
            if isinstance(v_r, Node_Select):
                o = Node_InSelect(v_l, v_r.select_spec)
                if op == "not in":
                    o = Node_Unary(child=o, operator="not")
            else:
                o = Node_Op(op, [v_l, v_r])
            return o
        if op in ("is", "is not"):
            o = Node_Op_Is(op)
        else:
            o = Node_Op(op)
        o.children.append(v_l)
        o.children.append(v_r)
        return o

    def parse_from_expr(self):
        """
        A specification for a source table, with aliases and joins.

        tableExpr :=
          table (alias) (( jointype table2 (alias2) 'on' condition ))

        jointype := (( inner | outer | right | left )) join
        """
        out = SqlSelect.FromExpr()
        out.table, out.alias, out.subquery = self._table_and_alias()
        tbl = out
        if self.peek_token(0) and self.peek_token(0).isPunct(','):
            # old style joins: table1, table2, ...
            while self.skip_punct(','):
                tbl.join = SqlSelect.Join()
                tbl = tbl.join
                tbl.table, tbl.alias, tbl.subquery = self._table_and_alias()
                tbl.joinType = {"cross"}
            return out
        # new style joins
        while self.cur_token():
            join = SqlSelect.Join()
            join.joinType = set()
            while self.cur_token() and self.cur_token().type == Token.KEYWORD and self.cur_token().value.lower() in FROM_JOIN_KEYWORDS:
                join.joinType.add(self.any_keyword("join type").lower())
            if not join.joinType:
                break
            join.table, join.alias, join.subquery = self._table_and_alias()
            if self.skip_keyword("on"):
                join.joinExpr = self.expect_expr()
            tbl.join = join
            tbl = join
        return out

    def _table_and_alias(self):
        subquery = None
        table = None
        if self._peek_test(0, "(") and self._peek_test(1, "select"):
            self.skip_punct("(")
            subquery = self.parse_select()
            if not subquery:
                self.report_error("expected select statement")
            self.skip_punct(")", error_if_missing=True)
        else:
            table = self.parse_table_name()
        alias = None
        if self.skip_keyword("as"):
            alias = self.any_keyword("alias")
        elif self.cur_token() and self.cur_token().type == Token.KEYWORD and self.cur_token().value.lower() not in self.FROM_RESERVED_KEYWORDS:
            alias = self.any_keyword("alias")
        return table, alias, subquery

    def parse_keyword_list(self):
        while True:
            yield self.any_keyword("field name")
            if not self.skip_punct(','):
                break

    def _parse_field_for_select(self, add_to_list):
        # detect '*' wildcard
        if self.skip_punct('*'):
            wildcard = "*"
            if self.skip_punct('?'):
                # TODO I think this was some kind of SQL extension but I can't find support for it elsewhere
                wildcard += "?"
            elif self.skip_punct('['):
                # custom SQL extension: all fields EXCEPT those listed here
                wildcard += "["
                wildcard += ",".join(self.parse_keyword_list())
                wildcard += "]"
                self.skip_punct(']', True)
            add_to_list.append((Node_Field((None, wildcard,)), None))
            return True
        # detect (table).* wildcard
        if self.peek_token(0).type == Token.KEYWORD and self.peek_token(2) and self.peek_token(
                1).value == "." and self.peek_token(2).value == '*':
            table_name = self.cur_token().value
            self.next_token()
            self.next_token()
            self.next_token()
            add_to_list.append((Node_Field((table_name, "*")), None))
            return True
        # otherwise, a field is an expression plus an optional alias
        calc = self.parse_expr()
        alias = None
        if not calc:
            return False
        if self.skip_keyword("as"):
            alias = self.any_keyword("field alias")
        elif self.cur_token() and self.cur_token().type == Token.KEYWORD and self.cur_token().value.lower() not in {
                'from', 'where', 'order', 'limit'
        }:
            alias = self.cur_token().value
            self.next_token()
        add_to_list.append((calc, alias))
        return True

    def parse_fields(self):
        """ Parses the part of a SELECT that defines the fields to extract """
        fields = []
        while self.cur_token():
            if not self._parse_field_for_select(fields):
                self.report_error("Expected field spec")
            if not self.skip_punct(','):
                break
        return fields

    def parse_group_by(self):
        if self.skip_keyword("group"):
            self.skip_keyword("by")
            group_by = SqlOrderBy()
            while self.cur_token():
                expr = self.expect_expr()
                group_by.addLevel(expr)
                if not self.skip_punct(','):
                    break
            return group_by

    def parse_order_by(self):
        if self.skip_keyword("order"):
            self.skip_keyword("by")
            order_by = SqlOrderBy()
            while self.cur_token():
                expr = self.expect_expr()
                asc = True
                if self.skip_keyword("ascending") or self.skip_keyword("asc"):
                    # valid
                    pass
                elif self.skip_keyword("descending") or self.skip_keyword("desc"):
                    asc = False
                order_by.addLevel(expr, asc)
                if not self.skip_punct(','):
                    break
            return order_by

    def parse_list_of_fields(self):
        fields = []
        if self.skip_punct('('):
            while True:
                if self.skip_punct(')'):
                    break
                # TODO quoting style is preserved in all cases but this one here
                field_names, quotes = self.parse_field_name()
                fields.append(field_names)
                if self.skip_punct(')'):
                    break
                self.skip_punct(',')
        return fields

    def _keyword_then(self, keyword: str, fn: callable, skip: bool=True):
        """
        A very useful shorthand.
        :param keyword:     Keyword to test for.
        :param fn:          Code to execute if it is found.
        :return:            Return value from fn(), or None.
        """
        if self.skip_keyword(keyword, skip=skip):
            expr = fn()
            return expr

    def _terms(self):
        return [
            ("from_expr", lambda: self._keyword_then("from", self.parse_from_expr)),
            ("where", lambda: self._keyword_then("where", self.expect_expr)),
            ("group_by", lambda: self._keyword_then("group", self.parse_group_by, skip=False)),
            ("having", lambda: self._keyword_then("having", self.expect_expr)),
            ("order_by", lambda: self._keyword_then("order", self.parse_order_by, skip=False)),
            ("start", lambda: self._keyword_then("offset", self.expect_expr)),
            ("limit", lambda: self._keyword_then("limit", self.expect_expr))
        ]

    def parse_select(self):
        """
        A 'select' statement.
        """
        if not self.skip_keyword("select"):
            return None
        out = self.compiled_class()
        if self.skip_keyword("distinct"):
            out.distinct = self.parse_list_of_fields()
        # parse field list
        out.fields = self.parse_fields()
        # process each part of the statement
        for attr, capture in self._terms():
            setattr(out, attr, capture())
        # selects can be combined with 'union'
        while self.skip_keyword("union"):
            out.union = []
            sel = self.parse_select()
            if not sel:
                self.report_error("expected SELECT")
            out.union.append(sel)
        return out

    def parse_select_only(self):
        """
        Parse a select statement and raise an exception if one is not found.  Also verifies that there is
        no garbage after the statement.
        """
        sel = self.parse_select()
        if not sel:
            self.report_error("Expected SELECT statement")
        self.skip_punct(";")
        if self.cur_token():
            self.report_error("Syntax error after statement")
        return sel

    def parse_read_statement(self):
        """
        Extension point for parsers that support read statements other than SELECT, like SHOW or DESCRIBE.
        """
        return self.parse_select_only()


def _get_select(sql_or_select, alt_parser=None):
    """
    Parses a select statement, or recognizes that the parameter is an already-parsed select statement.
    """
    if isinstance(sql_or_select, SqlSelect):
        return sql_or_select
    if sql_or_select not in compiler_cache_1:
        p = (alt_parser or SqlParser)(sql_or_select)
        parsed = p.parse_read_statement()
        compiler_cache_1[sql_or_select] = parsed
    return compiler_cache_1.get(sql_or_select)


def _lookup_tables_for_field_spec(select, field_spec, alias_to_table):
    """
    Find the tables associated with a wildcard.
    """
    if len(field_spec) > 1 and field_spec[-2]:
        # look up the table qualifying the wildcard
        table_ref = field_spec[:-1]
        tables = [table_ref]
        if not alias_to_table:
            alias_to_table = select.getAliasToTableMapping()
        if tables[0][-1] in alias_to_table:
            tables[0] = alias_to_table[tables[0][-1]]
    else:
        # search all tables in statement
        tables = find_referenced_tables(select, include_union=False, include_subselect=False, include_subquery=True)
    return tables or []


def expand_field_spec(select, field_spec, get_fields_for_table, alias_to_table=None):
    """
    Given the field specification of Node_Field, i.e. a tuple representing the parts of a
    reference to a field (i.e. a.b --> ("a","b")), look up that field and expand it into a consistent
    field specification, with fully normalized database, table and field components.  Aliases for field
    and table names are turned into proper field names, and wildcards are expanded.

    :param select:            A parsed SELECT statement.
    :param field_spec:         A tuple with at least a field name.
    :param get_fields_for_table: A method that will return a list of column names, given a table specification tuple.
    :param alias_to_table:      The alias-to-table mapping returned from SqlSelect (optional, to improve performance).
    :return:        A list of field specification 3-tuples.
    """
    if not field_spec[-1].startswith("*"):
        # just look up the field
        expanded = select.findFieldRef(field_spec, get_fields_for_table)
        return [expanded or field_spec]
    tables = _lookup_tables_for_field_spec(select, field_spec, alias_to_table=alias_to_table)
    out = []
    for table in tables:
        # 'table' can be the alias for a subquery
        sub = select.findSubqueryByAlias(table[-1])
        cols = []
        if sub:
            # descend to the subquery and enumerate its fields
            cols = expand_field_spec(sub, ("*",), get_fields_for_table)
            cols = [c[-1] for c in cols if c[-1]]
        elif get_fields_for_table:
            # or it can be the name of a real table, which we need to enumerate
            cols = get_fields_for_table(table) or []
        out += [table + (col,) for col in cols]
        # represent the wildcard/passthrough with a "" for the field name
        out.append(table + ("",))
    # custom language extension: the brackets let you exclude particular field names from the wildcard
    if field_spec[-1].startswith("*["):
        exclude = field_spec[-1][2:-1].split(',')
        out = filter(lambda x: x[-1] not in exclude, out)
    return out


def find_one_to_one_field_mappings(sql, get_fields_for_table=None):
    """
    For the given SQL, returns a mapping from output field name to a tuple describing
    the associated input field.  The tuples contain three components: database, table and field.

    Instead of a tuple, None will be mapped when there is no single field associated with the output.

    Returns None if the SQL did not contain a SELECT statement.

    There are a number of cases where getFieldsForTable is required in order for the results to be complete.
    These include when there are any wildcards and when there are multiple tables and fields without table
    qualifiers.
    """
    sel = _get_select(sql)
    out = {}
    alias_to_table = sel.getAliasToTableMapping()
    for field_spec in sel.fields:
        if not isinstance(field_spec[0], Node_Field):
            output_field_name = field_spec[1] or str(field_spec[0])
            out[output_field_name] = (None, None)
            continue
        expanded = expand_field_spec(sel, field_spec[0].fieldName, get_fields_for_table, alias_to_table=alias_to_table)
        if len(expanded) == 1:
            output_field_name = field_spec[1] or expanded[0][-1]
            out[output_field_name] = expanded[0]
            continue
        out.update({f[-1]: f for f in expanded if f[-1] is not None})
    return out


def find_output_columns(sql, get_fields_for_table=None):
    """
    Given a SELECT statement, return a list of all columns that it produces.
    """
    full_mapping = find_one_to_one_field_mappings(sql, get_fields_for_table)
    return full_mapping.keys()


class TableRefFinder(object):
    def __init__(self, include_union=True, include_subselect=True, include_subquery=True, alt_parser=None):
        self.include_union = include_union
        self.include_subselect = include_subselect
        self.include_subquery = include_subquery
        self.alt_parser = alt_parser
        self.out = OrderedDict()

    def refs_in_node(self, node):
        if not self.include_subselect:
            return
        if isinstance(node, Node_Select) or isinstance(node, Node_InSelect):
            self.refs_in_select(node.select_spec)
        elif hasattr(node, "children"):
            for sub in node.children:
                self.refs_in_node(sub)

    def refs_in_select(self, sel):
        # extensions provide a method to enumerate referenced tables
        if not isinstance(sel, SqlSelect):
            for tbl in sel.find_all_tables():
                self.out[tbl] = 1
            return
        tbl = sel.from_expr
        while tbl:
            if tbl.table:
                self.out[tbl.table] = 1
            elif tbl.subquery and self.include_subquery:
                self.refs_in_select(tbl.subquery)
            tbl = tbl.join
        if self.include_subselect:
            # NOTE: includeSubselect currently spans unions and subqueries whether you ask for it or not
            for expr in sel.allExpressions():
                self.refs_in_node(expr)
        if sel.union and self.include_union:
            for u in sel.union:
                self.refs_in_select(u)

    def find(self, sql):
        sel = _get_select(sql, alt_parser=self.alt_parser)
        self.refs_in_select(sel)
        return list(self.out.keys())


def find_referenced_tables(sql, include_union=True, include_subselect=True, include_subquery=True, alt_parser=None):
    """
    Given a SELECT statement, return a list of all tables that it references.

    :returns:  A list of tuples.  Each tuple contains the name of a database and the name of a table.  The
               databases will often be None, and the tables should never be None.
    """
    return TableRefFinder(include_union, include_subselect, include_subquery, alt_parser=alt_parser).find(sql)


class _FieldRefFinder(object):
    def __init__(self, get_fields_for_table=None):
        self.get_fields_for_table = get_fields_for_table
        self.out = set()

    def refs_in_node(self, select, node, alias_to_table):
        if isinstance(node, Node_Field):
            ref = select.findFieldRef(node.fieldName, self.get_fields_for_table)
            if not ref:
                ''' this is either an internal error in the SQL, or we don't have getFieldsForTable filled in,
                    either way we can't figure out which field is being referenced
                ref = node.fieldName
                if len(ref) == 1:
                    ref = (None,) + ref
                '''
                return
            expanded = expand_field_spec(select, ref, self.get_fields_for_table, alias_to_table=alias_to_table)
            for f in expanded:
                self.out.add(f)
        elif isinstance(node, Node_InSelect):
            self.refs_in_select(node.select_spec)
        if hasattr(node, "children"):
            for sub in node.children:
                self.refs_in_node(select, sub, alias_to_table)

    def refs_in_select(self, select):
        alias_to_table = select.getAliasToTableMapping()
        for expr in select.allExpressions(includeUnions=False, includeSubqueries=False):
            self.refs_in_node(select, expr, alias_to_table)
        tbl = select.from_expr
        while tbl:
            if tbl.subquery:
                self.refs_in_select(tbl.subquery)
            tbl = tbl.join
        if select.union:
            for u in select.union:
                self.refs_in_select(u)

    def find(self, sql: str):
        sel = _get_select(sql)
        self.refs_in_select(sel)
        # eliminate references to field aliases
        field_aliases = {fieldInfo[1] for fieldInfo in sel.fields if _field_spec_is_alias_only(fieldInfo)}
        if field_aliases:
            self.out = set(filter(lambda r: r[-1] not in field_aliases, self.out))
        return self.out


def find_referenced_fields(sql, get_fields_for_table=None):
    """
    Determine all input fields that are referenced in a given statement.  Returns 3-tuples for each field,
    with database, table and field names.
    """
    return _FieldRefFinder(get_fields_for_table=get_fields_for_table).find(sql)


def _expr_contains_field(expr, field_name):
    if isinstance(expr, Node_Field):
        if expr.fieldName[-1] == field_name:
            return True
    elif hasattr(expr, "children"):
        for child in expr.children:
            if _expr_contains_field(child, field_name):
                return True


def _field_spec_is_alias_only(field_spec):
    if not field_spec[1]:
        return False
    if isinstance(field_spec[0], Node_Field):
        if field_spec[0].fieldName[-1] == field_spec[1]:
            return False
        return True
    else:
        # If there is a field reference that matches the alias, the alias is only replacing the original field name
        #  and the original field name is still a valid field name.
        if _expr_contains_field(field_spec[0], field_spec[1]):
            return False
    return True



def find_excluded_wildcard_outputs(sql):
    """
    Find any fields that are specifically excluded from wildcard field selection.
    That is, for SQL like "select *[f1,f2] from t", it would return [f1,f2].
    This list would always be empty for normal SQL.
    :param sql: SQL to analyze (a SELECT statement).
    :return:    List of field names which will be excluded.
    """
    sel = _get_select(sql)
    out = set()
    for f in sel.fields:
        if not isinstance(f[0], Node_Field):
            continue
        if f[0].isWildcard():
            for f in f[0].getWildcardExceptions() or []:
                out.add(f)
        else:
            fn = f[0].fieldName
            if fn in out:
                out.remove(fn)
    return out


class SqlParserException(SqlException):
    def __init__(self, message, context, line, col, token):
        super(SqlParserException, self).__init__(message)
        self.context = context
        self.line = line
        self.col = col
        self.token = token

    def __str__(self):
        return u"{message}, line:col={line}:{col}, token={token}, context={context}".format(**self.__dict__)


# to speed up compilation
compiler_cache_1 = {}
# TODO get this working, currently it creates a recursive import problem
# compiler_cache_1 = LruCache(maxSize=1000)

FROM_JOIN_KEYWORDS = ["inner", "outer", "right", "left", "join", "full", "natural", "cross"]
FROM_RESERVED_KEYWORDS = FROM_JOIN_KEYWORDS + ["where", "union", "order", "offset", "limit", "group", "having", "on"]
