from .misc import sql_enquote_id, loose_table_match
from .eval_utils import cmp_table_names, find_field_in_list


class SqlSelect(object):
    """
    Parsed representation of a SELECT statement.
    """
    class FromExpr(object):
        def __init__(self):
            """
            table = a () with table components, i.e. db.schema.table, or just ('table'.)
            subquery = an SqlSelect instance
            alias = alternate name
            join - a Join instance
            """
            self.table = None
            self.subquery = None
            self.alias = None
            self.join = None

        def matchesTableRef(self, table_ref):
            # check database
            db_ref = table_ref[-2] if len(table_ref) > 1 else None
            if db_ref:
                if not self.table:
                    return False
                db = self.table[-2] if len(self.table) > 1 else None
                if not cmp_table_names(db_ref, db):
                    return False
            # check table name or alias
            if self.table and cmp_table_names(table_ref[-1], self.table[-1]):
                return True
            if self.alias and cmp_table_names(table_ref[-1], self.alias):
                return True
            return False

        def __str__(self):
            return self.to_sql()

        def to_sql(self, flavor: str=None):
            if self.subquery:
                return "({0})".format(self.subquery)
            out = SqlSelect._tblspec_to_sql(self.table, flavor)
            if self.alias:
                out += " AS " + self.alias
            if self.join:
                out += " " + self.join.to_sql(flavor)
            return out

    class Join(FromExpr):
        def __init__(self):
            """
            joinType = a collection of attributes like 'left', 'right', 'inner' or 'outer'
            joinExpr = a Node_Expr instance with the join condition
            """
            SqlSelect.FromExpr.__init__(self)
            self.joinType = set()
            self.joinExpr = None

        def __str__(self):
            return self.to_sql()

        def to_sql(self, flavor: str=None):
            out = " ".join(sorted(p for p in self.joinType if p != "join")).upper()
            out += " JOIN"
            if self.subquery:
                out += " ({0})".format(self.subquery.to_sql(flavor))
            if self.table:
                out += " " + SqlSelect._tblspec_to_sql(self.table, flavor)
            if self.alias:
                out += " AS " + self.alias
            if self.joinExpr:
                out += " ON " + self.joinExpr.to_sql(flavor)
            return out

    @staticmethod
    def _tblspec_to_sql(tblspec, flavor: str=None):
        if len(tblspec) > 1 and tblspec[0]:
            return ".".join(sql_enquote_id(p, flavor) for p in tblspec if p)
        else:
            return sql_enquote_id(tblspec[0], flavor)

    def __init__(self):
        """
        Create an object representation of a SQL SELECT statement.

        from_expr = Table or table expression which is the source of data.
        where = WHERE clause, i.e. filter
        fields = what to select - this is a [] of (expression, alias)
        group_by = a GroupBy instance
        having = a Node_Expr instance
        order_by = an OrderBy instance
        start = offset in rows from the beginning
        limit = maximum number of rows to fetch
        distinct = whether to eliminate duplicate rows - a [] of column names
        union = a [] of SqlSelect instances to concatenate
        """
        self.from_expr = None
        self.where = None
        self.fields = []
        self.group_by = None
        self.having = None
        self.order_by = None
        self.start = None
        self.limit = None
        self.distinct = None
        # a list of additional selects to union with this one
        self.union = None

    def getAllTables(self):
        out = []
        tbl = self.from_expr
        while tbl:
            if tbl.subquery:
                for t in tbl.subquery.getAllTables():
                    if t not in out:
                        out.append(t)
            elif tbl.table not in out:
                out.append(tbl.table)
            tbl = tbl.join
        if self.union:
            for u in self.union:
                out += u.getAllTables()
        return out

    def map_tables(self, replacer: callable, node=None):
        """
        Visit and replace/modify all table references.
        """
        tbl = node or self.from_expr
        while tbl:
            if tbl.subquery:
                tbl.subquery.map_tables(replacer)
            else:
                tbl.table = replacer(tbl.table)
            tbl = tbl.join
        for expr in self.allExpressions():
            self._map_tables_in_expr(replacer, expr)
        if self.union:
            for u in self.union:
                u.map_tables(replacer)

    def _map_tables_in_expr(self, replacer: callable, node):
        if hasattr(node, "select_spec"):
            self.map_tables(node.select_spec)
        elif hasattr(node, "children"):
            for sub in node.children:
                self._map_tables_in_expr(replacer, sub)

    def findSubqueryByAlias(self, alias):
        tbl = self.from_expr
        while tbl:
            if tbl.subquery and tbl.alias == alias:
                return tbl.subquery
            tbl = tbl.join

    def getAliasToTableMapping(self):
        """
        Generate a mapping of table aliases to full table names.
        """
        out = {}
        tbl = self.from_expr
        while tbl:
            #NOTE: we do not collect aliases for subqueries
            if tbl.alias and tbl.table:
                out[tbl.alias] = tbl.table
            tbl = tbl.join
        return out

    def isWildcard(self):
        """
        Detect a simple "*" wildcard that passes through every field.
        """
        if len(self.fields) != 1:
            return False
        f0 = self.fields[0][0]
        if not hasattr(f0, "fieldName") or f0.fieldName[-1] != "*":
            return False
        # joins complicate the meaning of 'simple pass-through'
        if self.from_expr.join:
            return False
        return True

    def _table_ref_only(self, field_ref, get_fields_for_table):
        """
        A table was specified, we can just look up the table, and assume the field is supposed to be there.
        """
        ref_table = field_ref[:-1]
        ref_field = field_ref[-1]
        tbl = self.from_expr
        while tbl:
            if tbl.matchesTableRef(ref_table):
                if tbl.subquery:
                    return tbl.subquery.findFieldRef(field_ref[-1:], get_fields_for_table, allow_implicit_match=False)
                return tbl.table + (ref_field,)
            tbl = tbl.join

    def _implicit_table_ref(self, field_ref, get_fields_for_table):
        """
        Handle the case where there are no joins, and therefore we know which table to search.
        """
        ref_field = field_ref[-1]
        if self.from_expr.subquery:
            return self.from_expr.subquery.findFieldRef(field_ref, get_fields_for_table, allow_implicit_match=False)
        return self.from_expr.table + (ref_field,)

    def findFieldRef(self, field_ref, get_fields_for_table=None, allow_implicit_match=True):
        """
        Given the field reference tuple from a Node_Field instance (a tuple of table name/alias and field name),
        return a 3-tuple that fully describes a field, listing the proper database name and table name, followed by
        the field name.
        """
        ref_table = _normalize_table_ref(field_ref[:-1])
        ref_field = field_ref[-1]
        # if there is no 'from', then no field reference can be satisfied, by definition
        if not self.from_expr:
            return None
        # if there is only one table (and if no table was specified) the association is clear
        if not ref_table[-1] and not self.from_expr.join and allow_implicit_match:
            return self._implicit_table_ref(field_ref, get_fields_for_table)
        # if a table reference was given we can just look it up and assume the field is in that table
        if ref_table[-1]:
            return self._table_ref_only(field_ref, get_fields_for_table)
        # find table by matching ref_field, using getFieldsForTable
        tbl = self.from_expr
        while tbl:
            if tbl.subquery:
                found = tbl.subquery.findFieldRef(field_ref, get_fields_for_table, allow_implicit_match=False)
                if found:
                    return found
            elif get_fields_for_table:
                col_names = get_fields_for_table(tbl.table)
                if loose_table_match(ref_field, col_names or []):
                    return tbl.table + (ref_field,)
            tbl = tbl.join

    def _exprs_in_details(self, includeUnions=True):
        """
        Enumerate expressions outside the main body of a SELECT.
        """
        if self.group_by:
            for level in self.group_by.levels:
                yield level[0]
        if self.order_by:
            for level in self.order_by.levels:
                yield level[0]
        if self.having:
            yield self.having
        if self.start:
            yield self.start
        if self.limit:
            yield self.limit
        for u in (self.union or []) if includeUnions else []:
            for expr in u.allExpressions():
                yield expr

    def allExpressions(self, includeSubqueries=True, includeUnions=True):
        """
        Iterate through all expressions in the statement.
        """
        for field in self.fields:
            yield field[0]
        tbl = self.from_expr
        while tbl:
            if includeSubqueries and tbl.subquery:
                for expr in tbl.subquery.allExpressions():
                    yield expr
            if hasattr(tbl, "joinExpr") and tbl.joinExpr:
                yield tbl.joinExpr
            tbl = tbl.join
        if self.where:
            yield self.where
        # check everywhere else
        for expr in self._exprs_in_details(includeUnions=includeUnions):
            yield expr

    def simplify(self, context):
        self.fields = [(expr.simplify(context), alias) for expr, alias in self.fields]
        if self.where:
            self.where = self.where.simplify(context)
        if self.having:
            self.having = self.having.simplify(context)
        if self.group_by:
            self.group_by.levels = [(expr.simplify(context), order) for expr, order in self.group_by.levels]
        if self.order_by:
            self.order_by.levels = [(expr.simplify(context), order) for expr, order in self.order_by.levels]
        if self.start:
            self.start = self.start.simplify(context)
        if self.limit:
            self.limit = self.limit.simplify(context)
        if self.union:
            self.union = [sel.simplify(context) for sel in self.union]
        # TODO also simplify the sub-expressions within 'from_expr'
        return self

    def ok_to_cache_as_subquery(self, context):
        """
        Test whether all the fields used in the expression can be satisfied by the given context.

        If so, it is assumed that nothing varies, and caching can be used.
        """
        for expr in self.allExpressions(includeSubqueries=False, includeUnions=True):
            if not self._node_ok_to_cache(expr, context):
                return False
        return True

    @staticmethod
    def _node_ok_to_cache(node, context):
        if hasattr(node, "fieldName"):
            f = node.fieldName
            if find_field_in_list(f, context) == -1:
                return False
            return True
        if hasattr(node, "children"):
            for child in node.children:
                if not SqlSelect._node_ok_to_cache(child, context):
                    return False
        return True

    def __str__(self):
        return self.to_sql()

    def to_sql(self, flavor: str=None):
        """
        Convert a SELECT to SQL.
        """
        # limit & offset do not work with mssql
        use_fetch = False
        use_top = False
        if flavor == "mssql":
            if self.limit and self.start is None:
                use_top = True
            elif self.limit or self.start:
                use_fetch = True
        # build...
        out = ["SELECT"]
        if use_top:
            out += ["TOP", self.limit.to_sql(flavor)]
        if self.distinct is not None:
            if len(self.distinct):
                out.append("DISTINCT(%s)" % ", ".join(map(lambda f: sql_enquote_id(f, flavor), self.distinct)))
            else:
                out.append("DISTINCT")
        f_spec = []
        for f in self.fields:
            part = f[0].to_sql(flavor)
            if f[1]:
                part += " AS " + sql_enquote_id(f[1], flavor)
            f_spec.append(part)
        out.append(", ".join(f_spec))
        if self.from_expr:
            out.append("FROM " + self.from_expr.to_sql(flavor))
        if self.where:
            out.append("WHERE {0}".format(self.where.to_sql(flavor)))
        if self.group_by:
            out.append("GROUP BY {0}".format(self.group_by.to_sql(flavor)))
        if self.having:
            out.append("HAVING {0}".format(self.having.to_sql(flavor)))
        if self.order_by:
            out.append("ORDER BY {0}".format(self.order_by.to_sql(flavor)))
        if use_top:
            # 'top' clause already emitted, no post-clause to add
            pass
        elif use_fetch:
            if not self.order_by:
                raise Exception(f"engine type {flavor}: cannot use offset without an order by")
            out += ["OFFSET", self.start.to_sql(flavor), "ROWS"]
            if self.limit:
                out += ["FETCH", "FIRST", self.limit.to_sql(flavor), "ROWS", "ONLY"]
        else:
            if self.start:
                out.append("OFFSET {0}".format(self.start.to_sql(flavor)))
            if self.limit:
                out.append("LIMIT {0}".format(self.limit.to_sql(flavor)))
        if self.union:
            out.append("UNION")
            out.append(" UNION ".join(u.to_sql(flavor) for u in self.union))
        return " ".join(out)


def _normalize_table_ref(table_ref):
    """
    Make sure a table reference has both a database name and a table name.
    """
    if len(table_ref) < 2:
        return (None,) + table_ref
    return table_ref
