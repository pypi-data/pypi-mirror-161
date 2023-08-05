import re
import inspect
from collections import defaultdict

from .compiled import Node_Op, Node_Field, Node_Unary, Node_Literal, Node_Function, Node_Op_Is, \
    Node_List, Node_Select, Node_InSelect, Node_Case, Node_Cast
from .exceptions import SqlException_NotImplemented
from .parser import SqlParser, TableRefFinder
from .select_stmt import SqlSelect
from .misc import sql_enquote_id, str_to_var_name
from .eval_utils import SqlEvaluationContext
from .expr_analysis import find_referenced_fields, find_groupby_fields, find_select_fields_pre_post, \
    find_orderby_fields, is_wildcard_all

EXTEND_SQL_RANDOM_SAMPLES = "random_samples"
MODE_QUERY_NUMEXPR = "query.numexpr"
MODE_QUERY_PYTHON = "query.python"
MODE_CALC_PANDAS = "calc.pandas"
MODE_CALC_DASK = "calc.dask"


class ExtendedSqlSelect(SqlSelect):
    def __init__(self):
        super(ExtendedSqlSelect, self).__init__()
        self.random_samples = None


class ExtendedSqlParser(SqlParser):
    """
    We extend SQL grammar a little to take advantage of some pandas functions like describe() and random sampling.

    NOTE: PostGres supports random sampling with its "TABLESAMPLE SYSTEM (n)" expression.
    """
    def __init__(self, sql):
        super(ExtendedSqlParser, self).__init__(sql, allow_any_function=True)
        self.compiled_class = ExtendedSqlSelect
        self.FROM_RESERVED_KEYWORDS.append(EXTEND_SQL_RANDOM_SAMPLES)

    def _terms(self):
        out = super(ExtendedSqlParser, self)._terms()
        for i, term in enumerate(out):
            if term[0] == "order_by":
                out.insert(i, ("random_samples", lambda: self._keyword_then(EXTEND_SQL_RANDOM_SAMPLES, self._parse_random_samples)))
                break
        return out

    def parse_read_statement(self):
        """
        Extension point for parsers that support read statements other than SELECT, like SHOW or DESCRIBE.
        """
        out = self.parse_describe()
        if not out:
            out = self.parse_select_only()
        return out

    def parse_describe(self):
        """
        We commandeer the DESCRIBE verb to access pandas.describe().

        DESCRIBE { dtypes() | percentiles(0.00, 0.05, 0.10, ...) } table_expression
        """
        if not self.skip_keyword("describe"):
            return
        out = SqlDescribe()
        while True:
            if self.skip_keyword("percentiles") and self.peek_token(0) and self.peek_token(0).value == "(":
                # TODO values should be numeric
                out.percentiles = self.parse_expr_or_list()
                if not isinstance(out.percentiles, Node_List):
                    self.report_error("expected list for 'percentiles'")
            elif self.skip_keyword("dtypes") and self.peek_token(0) and self.peek_token(0).value == "(":
                # TODO values are ignored - error if any given
                self.parse_expr_or_list()
                out.dtypes = True
            else:
                break
        # TODO parse include columns options
        out.include = "all"
        # parse table expression
        out.table_expr = self.parse_from_expr()
        return out

    def _parse_random_samples(self):
        """
        Parse custom 'random selection' SQL.  Format is...
            RANDOM_SAMPLES n
              If (n) is a positive integer it reflects the number of samples to take.  If it is a float between 0
              and 1, it is a percentage.
            RANDOM_SAMPLES PCT n
              n/100 is interpreted as above.
            RANDOM_SAMPLES PCT n STATE=123
              the 'state' value can be specified, and leads to a reproducible set of samples
        """
        rand_sel = RandomSamples()
        m = 1
        if self.skip_keyword('pct'):
            m = 0.01
        expr = self.expect_expr()
        rand_sel.count_or_percent = expr.eval(None)
        rand_sel.count_or_percent *= m
        if self.skip_keyword("state"):
            self.skip_punct('=', error_if_missing=True)
            rand_sel.random_state = self.expect_expr().eval(None)
        return rand_sel


class SqlDescribe(object):
    def __init__(self):
        # which tables - a 'FromExpr'
        self.table_expr = None
        self.percentiles = None
        self.include = None
        self.dtypes = False

    def find_all_tables(self):
        """
        Enumerate referenced tables.
        """
        sel = SqlSelect()
        sel.from_expr = self.table_expr
        refs = TableRefFinder()
        refs.refs_in_select(sel)
        return refs.out.keys()


class RandomSamples(object):
    """ Representation of our custom "RANDOM_SAMPLES" SQL extension """
    def __init__(self):
        self.count_or_percent = 0
        self.random_state = 0


class SqlToPandas(object):
    """
    Parses SQL and 'compiles' it into pandas/dask dataframe code.
    """
    def __init__(self, sql: str, local_tables: (callable, str)="tables", ext_table_access: callable=None,
                 tmpvar: str="_",
                 select=None, ext_vars=None, parent=None, external_processing: dict=None, pandas_only: bool=False):
        """
        :param sql:                 SQL to compile.
        :param local_tables:        Name of a {} where local tables are stored, blank for local variables, or a callable to generate code.
        :param ext_table_access:    Code generator for access to external tables.
        :param tmpvar:              The name of the variable used to store the query-in-progress.
        :param select:              The parsed SELECT statement to compile.
        :param ext_vars:            Variables in the SELECT statement reference with "@name".
        :param parent:              Parent instance, indicating this is a subquery.
        :param external_processing: Indicates caller's willingness to do some of the work.  Specifically the
                                    field 'post_limit', if supplied, will be filled in with a number of rows from
                                    a simple LIMIT.
        :param pandas_only:         Flag indicating we can simplify code and assume all dataframes are pandas (not dask).
        """
        self.tmpvar = tmpvar
        self.sql = sql
        self.parent = parent
        self.external_processing = external_processing or {}
        self.pandas_only = pandas_only
        self.code = ""
        self.before = []
        self.after = []
        self.misc_imports = set()
        self.depth = 0 if not parent else parent.depth + 1
        self.referenced_tables = set()
        # when columns are changed, i.e. df[new_col] += 1, we risk changing the underlying table
        self.columns_modified = False
        self.local_tables = local_tables
        self.ext_table_access = ext_table_access
        if isinstance(ext_vars, SqlEvaluationContext):
            self.eval_context = ext_vars
        else:
            self.eval_context = SqlEvaluationContext(ext_vars=ext_vars)
        if select:
            self.compile_select(select)
            return
        parser = ExtendedSqlParser(sql)
        descr = parser.parse_describe()
        if descr:
            self.compile_describe(descr)
            return
        self.compile_select(parser.parse_select_only())
        # final step: make code a bit more readable
        self.more_readable()
        # prepend imports
        if self.misc_imports:
            self.code = "\n".join(f"import {pkg}" for pkg in sorted(self.misc_imports)) + "\n" + self.code

    def compile_describe(self, descr):
        # fill in arguments
        args = []
        if descr.percentiles:
            args.append("percentiles=[%s]" % ", ".join(map(str, descr.percentiles.children)))
        if descr.include:
            args.append("include=%s" % repr(descr.include))
        # start building description
        expr = ""
        if not self.pandas_only:
            expr += inspect.getsource(_to_pandas)
        expr += f"{self.tmpvar} = {self._process_from(descr.table_expr)}\n"
        expr += f"_d = {self.tmpvar}.describe({', '.join(args)})"
        # TODO append() is deprecated - have to detect dask/pandas and use pandas.concat() or dask.dataframe.concat()
        if self.pandas_only:
            expr += f".append({self.tmpvar}.isna().sum().to_frame('nulls').transpose())"
        else:
            expr += f".append(_to_pandas({self.tmpvar}.isna().sum().to_frame('nulls')).transpose())"
        if descr.dtypes:
            if self.pandas_only:
                expr += f".append({self.tmpvar}.dtypes.to_frame('dtype').transpose())"
            else:
                expr += f".append(_to_pandas({self.tmpvar}.dtypes.to_frame('dtype')).transpose())"
            expr += "\n_d = _d.astype(str)"
        expr += "\n_d['_metric_'] = _d.index\n"
        expr += f"{self.tmpvar} = _d"
        self._finish(expr)

    def compile_select(self, select):
        select.simplify(self.eval_context)
        # build all the qualifications around the selected table
        self.process_select(select)
        # get the table
        from_expr = self._process_from(select.from_expr)
        if not self.columns_modified:
            # if we don't change any columns a simple slice will do to prevent changing the original
            tbl_expr = "{v} = {from_expr}[:]".format(v=self.tmpvar, from_expr=from_expr)
        elif self.pandas_only:
            tbl_expr = "{v} = {from_expr}.copy()".format(v=self.tmpvar, from_expr=from_expr)
        else:
            # in pandas there is a member function to copy, in dask we use copy.copy
            tbl_expr = \
                "{v} = {from_expr}\n" \
                "{v} = {v}.copy() if hasattr({v}, 'copy') else copy.copy({v})\n".format(
                v=self.tmpvar, from_expr=from_expr
            )
        self._finish(tbl_expr)

    def _finish(self, tbl_expr):
        # put it together
        if "\n" in tbl_expr:
            # multi-line 'from' has to be separated from qualifiers
            self.code = "%s\n%s = %s" % (tbl_expr, self.tmpvar, self.tmpvar) + self.code
        else:
            # single line 'from' expression can be joined to qualifiers
            self.code = tbl_expr + self.code
        self.code = "\n".join(["\n".join(self.before), self.code, "\n".join(reversed(self.after))])
        self.code = re.sub(r'(^|\n)%s = %s(\n|$)' % (self.tmpvar, self.tmpvar), "\n", self.code)
        self.code = self.code.replace("\n\n", "\n")
        self.code = self.code.strip("\n") + "\n"
        if self.sql:
            self.code = "# SQL: %s\n%s" % (repr(self.sql), self.code)

    def access_table(self, table_ref: tuple):
        # local table - lookup in the specified {}
        if len(table_ref) == 1 or not table_ref[-2]:
            table_name = table_ref[-1]
            if not self.local_tables:
                return "%s" % table_name
            if isinstance(self.local_tables, str):
                return "%s[%s]" % (self.local_tables, repr(table_name))
            return self.local_tables(table_name)
        # external table - call supplied handler
        if not self.ext_table_access:
            self.err("external tables not supported: %s" % repr(table_ref))
        setup, code = self.ext_table_access(table_ref)
        if setup and setup not in self.before:
            self.before.append(setup)
        return code

    def sub_inst(self, tmpvar: str, select=None):
        return SqlToPandas(
            sql="", local_tables=self.local_tables, ext_table_access=self.ext_table_access,
            tmpvar=tmpvar, select=select, parent=self
        )

    def _process_from(self, from_expr):
        if not from_expr:
            self.err("FROM clause is required")
        if from_expr.subquery:
            v_wrap = "_%d" % len(self.before)
            sub = self.sub_inst(tmpvar=v_wrap, select=from_expr.subquery)
            self.before.append(sub.code)
            self.after.append("del %s" % v_wrap)
            code = v_wrap
        else:
            self.referenced_tables.add(from_expr.table)
            code = self.access_table(from_expr.table)
        if not from_expr.join:
            return code
        other = self._process_from(from_expr.join)
        # 'join_fields': table > list[str] -- fields being used from each table
        join_fields = defaultdict(list)
        # find columns to join on, verify it's a simple join
        self.split_join_on(from_expr.join.joinExpr, join_fields)
        # figure out which table named in the join is which
        from_tbl = from_expr.table[-1] if from_expr.table else None
        join_tbl = from_expr.join.table[-1] if from_expr.join.table else None
        f_l = join_fields.get(from_expr.alias or from_tbl, join_fields.get(from_tbl))
        f_r = join_fields.get(from_expr.join.alias or join_tbl, join_fields.get(join_tbl))
        if not f_l or not f_r:
            self.err("could not connect join.on fields to tables: %s" % str(from_expr))
        # TODO if 'multi_key' is set, and result would be dask, raise an exception
        multi_key = len(f_l) != 1 or len(f_r) != 1
        if len(f_l) == 1:
            f_l = f_l[0]
        if len(f_r) == 1:
            f_r = f_r[0]
        how = self._find_join_type(from_expr)
        # left has to be dask if right is dask
        code += \
            "\n" \
            "_r = {other}\n".format(other=other)
        if not self.pandas_only:
            self.misc_imports.add("pandas")
            code += \
                "if isinstance({v}, pandas.DataFrame) and 'dask' in _r.__class__.__name__:\n" \
                "    {v} = daskdataframe.from_pandas({v}, chunksize=10000000)\n".format(
                    v=self.tmpvar, other=other
                )
        # finally, do the join
        code += "{v} = {v}.join(_r.set_index({f_r}, drop=False), on={f_l}, how={how}, rsuffix='_r')".format(
            v=self.tmpvar, other=other, f_r=repr(f_r), f_l=repr(f_l), how=repr(how)
        )
        return code

    def _find_join_type(self, from_expr):
        how = None
        for j_type in ["right", "inner", "outer", "left"]:
            if j_type in from_expr.join.joinType:
                how = j_type
                break
        if not how:
            self.err("unsupported join type: %s" % from_expr.join.joinType)
        return how

    def _process_groupby(self, group_by, aggs, non_agg_cols):
        group_fields = []
        for n_lvl, lvl in enumerate(group_by.levels):
            if not lvl[1]:
                self.err("only ascending groupings are allowed")
            group_fields.append("_agx_%d_%d" % (self.depth, n_lvl))
        # reconstruct
        self.misc_imports.add("pandas")
        lines = [
            "",
            "_g = %s.groupby(%s)" % (self.tmpvar, repr(group_fields)),
            # Big dask dataframes get reduced to a single in-memory dataframe
            "%s = pandas.DataFrame()" % self.tmpvar
        ]
        # TODO support large post-aggregation results
        '''
        In order to support large aggregate results...
        1) create new dask dataframe from the new groupby (_g)'s index, specifying number of partitions:
           _ = _g[{group_fields}].first(split_to=..., split_every=...).to_frame()
        2) assign each column as below, but make sure split_to matches in every case
        3) and, of course, we have to actually choose a value for split_out
           could be max(_.npartitions//4, 1) <-- or something like that

        See: https://examples.dask.org/dataframes/02-groupby.html#Many-groups
        '''
        # pull in the aggregated fields
        for agg_var, agg_expr in aggs:
            lhs = "%s[%s]" % (self.tmpvar, repr(agg_var))
            lines.append(self.render_calc(lhs, agg_expr, mode="aggregate"))
        # carry forward all the non-aggregate fields
        for col in non_agg_cols:
            lines.append("%s[%s] = _g[%s].first()" % (self.tmpvar, repr(col), repr(col)))
        lines.append("del _g")
        lines.append("_ = _")
        return "\n".join(lines)

    def _process_groupby_all(self, aggs, non_agg_cols):
        build = []
        if not self.pandas_only and "def _compute(df):" not in self.before:
            self.before += [
                "def _compute(df):",
                "    if hasattr(df, 'compute'):",
                "        return df.compute()",
                "    return df"
            ]
        # pull in the aggregated fields
        for agg_var, agg_expr in aggs:
            node_code = self.render_node(agg_expr, mode="aggregate")
            if not self.pandas_only:
                node_code = f"_compute({node_code})"
            build.append("%s: [%s]" % (repr(agg_var), node_code))
        # carry forward all the non-aggregate fields
        for col in non_agg_cols:
            build.append("%s: _g[%s].head(1)" % (repr(col), repr(col)))
        self.misc_imports.add("pandas")
        lines = [
            "",
            "_g = %s" % self.tmpvar,
            "%s = pandas.DataFrame({%s})" % (self.tmpvar, ", ".join(build)),
            "del _g",
            "_ = _"
        ]
        return "\n".join(lines)

    def _process_orderby(self, order_by, field_map):
        if not order_by:
            return ""
        exprs, orders = zip(*order_by.levels)
        expr_fields = []
        for expr in exprs:
            if not isinstance(expr, Node_Field):
                self.err("only single field supported for order by")
            expr_fields.append((field_map or {}).get(tuple(expr.fieldName), expr.fieldName[-1]))
        fields_repr = repr(expr_fields)
        asc = True
        if all(orders):
            """ all ascending """
            pass
        elif not any(orders):
            """ all descending """
            asc = False
        else:
            self.err("mixed asc/desc not supported yet")
        if self.pandas_only:
            out = ".sort_values({fields}, ascending={asc}).set_index({field1}, drop=False)\n".format(
                    fields=fields_repr, field1=repr(exprs[0].fieldName[-1]), asc=asc
                )
        else:
            self.misc_imports.add("pandas")
            out = \
                "\n" \
                "if isinstance({v}, pandas.DataFrame):\n" \
                "    {v} = {v}.sort_values({fields}, ascending={asc})\n" \
                "else:\n".format(
                    v=self.tmpvar, fields=fields_repr, asc=asc
                )
            if not asc:
                out += "    raise Exception('descending sort not supported in dask mode')\n"
            elif len(exprs) > 1:
                out += "    raise Exception('multi-key sort not supported in dask mode')\n"
            else:
                out += "    {v} = {v}.set_index({field1}, drop=False)\n".format(
                    v=self.tmpvar, field1=repr(exprs[0].fieldName[-1])
                )
            out += "{v} = {v}".format(v=self.tmpvar)
        return out

    def _process_range(self, select):
        start = select.start.eval(self.eval_context) if select.start else 0
        limit = select.limit.eval(self.eval_context) if select.limit else -1
        lo = start or ""
        if start and limit != -1:
            hi = start + limit
        else:
            hi = limit if limit != -1 else ""
        if not lo and hi and "post_limit" in self.external_processing:
            # caller is willing to truncate results
            self.external_processing["post_limit"] = hi
            return ""
        if lo or hi:
            if self.pandas_only:
                out = ".iloc[{lo}:{hi}]".format(lo=lo, hi=hi)
            else:
                self.misc_imports.add("pandas")
                out = \
                    "\n" \
                    "if isinstance({v}, pandas.DataFrame):\n" \
                    "    {v} = {v}.iloc[{lo}:{hi}]\n" \
                    "else:\n".format(
                        v=self.tmpvar, lo=lo, hi=hi
                    )
                if hi:
                    out += \
                        "    {v} = {v}.head({hi}, npartitions=-1, compute=False)\n".format(
                            v=self.tmpvar, hi=hi
                        )
                if lo:
                    # TODO tail() only works on the last partition, so really large chunks will be truncated
                    #  - it would be better to raise an exception than to silently return bad data
                    out += \
                        "    _nr = {v}.shape[0].compute()\n" \
                        "    {v} = {v}.tail(max(_nr - {start}, 0), compute=False)\n".format(
                            v=self.tmpvar, start=start
                        )
                out += "{v} = {v}".format(v=self.tmpvar)
            return out
        return ""

    def _process_random_samples(self, random_samples):
        if not random_samples:
            return ""
        args = []
        n = random_samples.count_or_percent
        if n < 1:
            args.append("frac=%s" % repr(n))
        else:
            args.append("n=%s" % repr(int(n)))
        if random_samples.random_state:
            args.append("random_state=%s" % repr(int(random_samples.random_state)))
        return ".sample(%s)" % ", ".join(args)

    def _process_union(self, selects):
        if not selects:
            return ""
        # TODO protect from nested unions
        prefix = "_u"
        table_vars = []
        code_out = "\n"
        for n_sel, other_sel in enumerate(selects):
            u_var = prefix + "%d" % (n_sel+1)
            tbl_code = SqlToPandas(
                sql="", local_tables=self.local_tables, ext_table_access=self.ext_table_access,
                tmpvar=u_var, select=other_sel, ext_vars=self.eval_context
            ).code
            code_out += tbl_code
            #if not code_out.endswith("\n"):
            #    code_out += "\n"
            table_vars.append(u_var)
        table_vars.append(self.tmpvar)
        # result has to be dask if any sub-tables are dask
        self.misc_imports.add("pandas")
        if self.pandas_only:
            code_out += "{v} = pandas.concat([{tbls}], sort=False)".format(v=self.tmpvar, tbls=', '.join(table_vars))
        else:
            self.misc_imports.add("dask.dataframe")
            code_out += \
                "_union = dask.dataframe.concat if not all(isinstance(sub, pandas.DataFrame) for sub in %s) \\\n" \
                "    else (lambda tbls: pandas.concat(tbls, sort=False))\n" % repr(table_vars)
            code_out += "{v} = _union([{tbls}])\n{v} = {v}".format(
                v=self.tmpvar, tbls=", ".join(table_vars)
            )
        return code_out

    def _process_distinct(self, distinct):
        if distinct is None:
            return ""
        subset = ""
        if len(distinct):
            subset = ", ".join(repr(f[-1]) for f in distinct)
        return ".drop_duplicates(%s)" % subset

    def process_select(self, select):
        # analyze fields used in each part of the statement
        field_analysis = FieldAnalysis(select, depth=self.depth)
        # we might need to carry forward some fields for the WHERE/GROUP/ORDER clauses
        aggs = []
        non_agg_cols = []
        fb = FieldsBuilder(self, aggs, non_agg_cols)
        del_after_where = set()
        del_cols = set()
        field_map = {}
        if not field_analysis.sel_wildcard:
            field_analysis.analyze()
            del_cols = field_analysis.del_cols
            del_after_where = field_analysis.del_after_where
            fb.after_field_map = field_map = field_analysis.field_map
            # calculate group-by expressions
            gb_exprs = field_analysis.analyze_groupby()
            # do calculations, etc.
            self.code += fb.build(select.fields, field_analysis.temp_exprs, gb_exprs)
        if select.where:
            self.code += self.render_query(select.where, field_map=field_map)
        if del_after_where:
            self.code += ".drop(columns=%s)" % repr(del_after_where)
        if select.group_by:
            self.code += self._process_groupby(select.group_by, aggs, non_agg_cols)
        elif aggs:
            self.code += self._process_groupby_all(aggs, non_agg_cols)
        if select.having:
            self.code += self.render_query(select.having, field_map=field_map)
        self.code += self._process_distinct(select.distinct)
        self.code += self._process_random_samples(select.random_samples)
        self.code += self._process_orderby(select.order_by, field_map)
        self.code += self._process_range(select)
        if del_cols:
            # drop the temporary columns used by group/order
            self.code += ".drop(columns=%s)" % repr(del_cols)
        self.code += self._process_union(select.union)

    def err(self, message):
        raise SqlException_NotImplemented(message)

    def _render_op(self, node, mode, field_map):
        op_map_calc = {
            "||": "|", "=": "==", "<>": "!=",
            "and": "&", "or": "|", "&&": "&",
        }
        op_map_query = {
            "||": "|", "=": "==", "<>": "!=",
            "&&": "&",
        }
        op_map = op_map_query if mode.startswith("query") else op_map_calc
        op_bad = {
            "like", "not like", "regexp", "not regexp", "match", "not match"
        }
        op = node.operator
        if op in op_bad:
            self.err("operator not supported yet: %s" % node.operator)
        if op == "in" and mode != MODE_QUERY_NUMEXPR:
            return "%s.isin(%s)" % (
                self.render_node(node.children[0], mode, field_map),
                self.render_node(node.children[1], mode, field_map)
            )
        # checks for NULL
        if op in {Node_Op_Is.OP_IS, Node_Op_Is.OP_IS_NOT} and mode.startswith("query"):
            if isinstance(node.children[1], Node_Literal) and node.children[1].value is None:
                if mode == MODE_QUERY_NUMEXPR:
                    raise CantUseNumExpr()
                return "%s(%s).isnull()" % ("not " if op == Node_Op_Is.OP_IS_NOT else "", self.render_node(node.children[0], mode, field_map))
            # TODO may not make sense - what are other valid uses of 'is'?
            # try mapping to =/!=
            op = {Node_Op_Is.OP_IS: "=", Node_Op_Is.OP_IS_NOT: "!="}[op]
        op = op_map.get(op, op)
        return "(%s)" % (" " + op + " ").join(map(lambda n: self.render_node(n, mode, field_map), node.children))

    def _render_fn(self, node, mode, field_map):
        fn = node.functionName
        if node.isAggregate() and mode == "aggregate":
            return self._render_fn__aggregate(node, fn)
        if mode in {"query", MODE_QUERY_NUMEXPR, MODE_QUERY_PYTHON}:
            return self._render_fn__query(fn, node, mode, field_map)
        elif mode == MODE_CALC_DASK and fn == "if":
            # compensate for dask bug - https://github.com/dask/dask/issues/5839
            self.misc_imports.add("dask.array")
            return "dask.array.where(({arg0}).values, {args})".format(
                arg0=self.render_node(node.children[0], mode, field_map),
                args=", ".join(self.render_node(child, mode, field_map) for child in node.children[1:]),
            )
        elif mode in {MODE_CALC_PANDAS, MODE_CALC_DASK} and fn in NUMPY_FUNCTIONS:
            lib = "numpy" if mode == MODE_CALC_PANDAS else "dask.array"
            self.misc_imports.add(lib)
            return "{lib}.{fn}({args})".format(
                lib=lib,
                fn=NUMPY_FUNCTIONS[fn],
                args=", ".join(self.render_node(child, mode, field_map) for child in node.children),
            )
        elif mode == "calc":
            """
            For 'calc' mode, we start with the set of functions we can use without recourse to numpy/dask.array.
            """
            r = self._render_fn__calc(fn, node, mode, field_map)
            if r:
                return r
        self.err("function not supported yet: %s" % node.functionName)

    def _render_fn__aggregate(self, node, fn):
        """
        Compile aggregation function calls.
        """
        fn = AGGREGATES.get(fn, fn)
        if fn == "count" and len(node.children) == 1 and str(node.children[0]) == "*":
            return "_g.count().min(axis=int(_g.__class__.__name__ != 'DataFrame'))"
        varname = str_to_var_name("_agg_" + str(node.children[0]))
        return "_g[%s].%s()" % (repr(varname), fn)

    def _render_fn__query(self, fn, node, mode, field_map):
        """
        Render functions in the context of pandas.query().
        """
        #  https://numexpr.readthedocs.io/projects/NumExpr3/en/latest/user_guide.html#supported-functions
        if fn in QUERY_FUNCTIONS:
            return "%s(%s)" % (QUERY_FUNCTIONS[fn], ", ".join(self.render_node(child, mode) for child in node.children))
        if fn in QUERY_SUB_FUNCTIONS:
            return "%s.%s(%s)" % (
                self.render_node(node.children[0], mode, field_map),
                QUERY_SUB_FUNCTIONS[fn],
                ", ".join(self.render_node(child, mode, field_map) for child in node.children[1:])
            )
        if fn in (set(NATIVE_FUNCTIONS) | set(NATIVE_PROPERTIES) | set(NUMPY_FUNCTIONS)):
            raise NeedToUseCalc

    def _render_fn__calc(self, fn, node, mode, field_map):
        """
        Render a function call in "calc" mode, which uses overloaded pandas operators to do a piecewise
        query.
        """
        if fn in NATIVE_FUNCTIONS:
            # these functions can be coded identically in pandas or dask
            fn = NATIVE_FUNCTIONS[fn]
            return "(%s).%s(%s)" % (
                self.render_node(node.children[0], mode, field_map),
                fn,
                ", ".join(self.render_node(child, mode, field_map) for child in node.children[1:])
            )
        elif fn in NATIVE_PROPERTIES:
            fn = NATIVE_PROPERTIES[fn]
            return "(%s).%s" % (
                self.render_node(node.children[0], mode, field_map),
                fn
            )
        elif fn in NUMPY_FUNCTIONS:
            # but not these
            raise NeedToBifurcate()

    def _render_case(self, node, mode, field_map: dict=None):
        """
        CASE statement.
        """
        # convert the case statement to a bunch of if() functions
        when_then_else = node.children
        pairs = []
        for n in range(0, len(when_then_else)-1, 2):
            pairs.append((when_then_else[n], when_then_else[n+1]))
        pairs.reverse()
        out = when_then_else[-1] if len(when_then_else) % 2 else Node_Literal(None)
        for cond, if_1 in pairs:
            out = Node_Function("if", [cond, if_1, out])
        # render it
        return self._render_fn(out, mode, field_map)

    def render_query(self, node, field_map: dict=None):
        """
        Apply a filter (i.e. a WHERE clause) to the current table.
        """
        try:
            try:
                return ".query(%s)" % repr(self.render_node(node, mode=MODE_QUERY_NUMEXPR, field_map=field_map))
            except CantUseNumExpr:
                return ".query(%s, engine='python')" % repr(self.render_node(node, mode=MODE_QUERY_PYTHON, field_map=field_map))
        except NeedToUseCalc:
            calc = self.render_calc("_filt", node, field_map=field_map)
            self.after.append("del _filt")
            return "\n" + calc + "{v} = {v}[_filt]".format(v=self.tmpvar)

    def render_calc(self, lhs, node, mode: str="calc", field_map: dict=None):
        """
        Perform a calculation and assign it to the given LHS (left hand side).
        """
        try:
            return "%s = %s\n" % (lhs, self.render_node(node, mode=mode, field_map=field_map))
        except NeedToBifurcate:
            pandas_calc = self.render_node(node, mode=mode+".pandas", field_map=field_map)
            if self.pandas_only:
                return \
                    "{lhs} = {pandas_calc}\n".format(
                    lhs=lhs, pandas_calc=pandas_calc
                )
            self.misc_imports.add("pandas")
            return \
                "if isinstance({v}, pandas.DataFrame):\n" \
                "    {lhs} = {pandas_calc}\n" \
                "else:\n" \
                "    {lhs} = {dask_calc}\n".format(
                    v=self.tmpvar, lhs=lhs,
                    pandas_calc=pandas_calc,
                    dask_calc=self.render_node(node, mode=mode+".dask", field_map=field_map)
                )

    def render_node(self, node, mode: str=MODE_QUERY_NUMEXPR, field_map: dict=None):
        """
        Render an SQL expression.

        x < 4:
          mode==query:    x < 4           (i.e. for use inside DataFrame.query())
          mode==calc:  _['x'] + 1         (i.e. for computing a column)
        """
        if isinstance(node, (Node_Op, Node_Op_Is)):
            return self._render_op(node, mode, field_map)
        if isinstance(node, Node_Field):
            field_name = (field_map or {}).get(tuple(node.fieldName), node.fieldName[-1])
            if mode.startswith("query"):
                return sql_enquote_id(field_name, "mysql")
            else:
                return "%s[%s]" % (self.tmpvar, repr(field_name))
        if isinstance(node, Node_Unary):
            return "%s %s" % (node.operator, self.render_node(node.children[0], mode, field_map=field_map))
        if isinstance(node, Node_Literal):
            return repr(node.value)
        if isinstance(node, Node_Cast):
            pandas_type = SQL_TYPES_TO_PANDAS_TYPES.get(node.to_type, node.to_type)
            return "%s.astype(%s, errors='ignore')" % (
                self.render_node(node.children[0], mode, field_map=field_map), repr(pandas_type)
            )
        if isinstance(node, Node_Function):
            return self._render_fn(node, mode, field_map)
        if isinstance(node, Node_Case):
            return self._render_case(node, mode, field_map)
        if isinstance(node, Node_InSelect):
            v_wrap = "_%d" % len(self.before)
            sub = self.sub_inst(tmpvar=v_wrap, select=node.select_spec)
            self.before.append(sub.code)
            self.before.append("{sub} = set({sub}[{sub}.columns[0]])".format(sub=v_wrap))
            self.after.append("del %s" % v_wrap)
            return self.render_node(node.children[0], mode, field_map=field_map) + ".isin(%s)" % v_wrap
        if isinstance(node, Node_Select):
            v_wrap = "_%d" % len(self.before)
            sub = self.sub_inst(tmpvar=v_wrap, select=node.select_spec)
            self.before.append(sub.code)
            return "{tbl}[{tbl}.columns[0]].max()".format(tbl=v_wrap)
        ''' TODO it isn't clear to me when this is used in a SELECT
        if isinstance(node, Node_List):
            subs = [self.render_node(sub, mode=mode, field_map=field_map) for sub in node.children]
            return "(" + "".join(f"{sub}, " for sub in subs) + ")"
        '''
        self.err("node type not supported yet: %s" % node.__class__.__name__)

    def split_join_on(self, node, out):
        if isinstance(node, Node_Field):
            if len(node.fieldName) < 2:
                self.err("joins require aliases for sub-selects")
            tbl = node.fieldName[-2]
            fld = node.fieldName[-1]
            out[tbl].append(fld)
            return
        elif isinstance(node, Node_Op):
            if node.operator not in {"=", "==", "and"}:
                self.err("unsupported operation for join.on: %s" % node.operator)
        else:
            self.err("unsupported for join.on: %s" % node.__class__.__name__)
        if hasattr(node, "children"):
            for sub in node.children:
                self.split_join_on(sub, out)

    def more_readable(self):
        # copy-all-columns, followed by copy-some-columns, i.e. [:][['a', 'b']]
        self.code = re.sub(r"\[:\](\[\['[^'\n]+'(, '[^'\n]+')*\]\])", r'\1', self.code)


class FieldAnalysis(object):
    def __init__(self, select, depth: int):
        self.select = select
        self.depth = depth
        self.sel_wildcard = is_wildcard_all(select.fields)
        self.del_after_where = set()
        self.del_cols = set()
        self.field_map = {}
        self.temp_exprs = []

    def analyze(self):
        """
        Work out which fields need to be 'carried forward' from our input table, to be used by WHERE, GROUP BY, etc..

        For example...
          SELECT a, b FROM table WHERE c=1

          Here, the 'c' column is not preserved in the field list but it is neededby the WHERE clause.
        """
        sel_in_fields, sel_out_fields = find_select_fields_pre_post(self.select.fields)
        where_fields = find_referenced_fields(self.select.where)
        groupby_fields = find_groupby_fields(self.select.group_by)
        orderby_fields = find_orderby_fields(self.select.order_by)
        preserve_w = where_fields - set(sel_out_fields)
        preserve_g_o = (groupby_fields | orderby_fields) - set(sel_out_fields)
        preserve_o = orderby_fields - set(sel_out_fields)
        preserve = preserve_w | preserve_g_o
        for nf, f in enumerate(preserve):
            fn = "_tmp_%d" % nf
            self.field_map[f] = fn
            if f in preserve_w and f not in preserve_g_o:
                self.del_after_where.add(fn)
            elif f in preserve_o:
                self.del_cols.add(fn)
            self.temp_exprs.append((Node_Field(f), fn))

    def analyze_groupby(self):
        """
        Calculate all the group-by values and store them in temporary columns.
        """
        gb_exprs = []
        for n_level, level in enumerate(self.select.group_by.levels if self.select.group_by else []):
            fn = "_agx_%d_%d" % (self.depth, n_level)
            gb_exprs.append((level[0], fn))
        return gb_exprs


def aggregate_exprs(node, out):
    if isinstance(node, Node_Function) and node.isAggregate():
        expr = node.children[0]
        out[str(expr)] = expr
        return True
    found = False
    if hasattr(node, "children"):
        for sub in node.children:
            found = found or aggregate_exprs(sub, out)
    return found


AGGREGATES = {
    "min": "min",
    "max": "max",
    "count": "count",
    "count_distinct": "nunique",
    "sum": "sum",
    "total": "sum",
    "avg": "mean",
    "average": "mean",
    "median": "median",
    "stdev": "std",
    # TODO more pandas functions: mode(), var()
}


class FieldsBuilder(object):
    """
    Compiles the field selection/calculation of an SQL SELECT, i.e. "select _____ from ..."
    """
    def __init__(self, s2p, aggs, non_agg_cols):
        """
        :param s2p:             The sql-to-pandas compilation that is in progress.
        :param aggs:            All of the fields which are calculated based on aggregation (i.e. the
                                fields whose expressions contain aggregation functions like 'avg' or 'sum')
                                are listed in the provided [].  A [] of (alias, expression) is stored here.
        :param non_agg_cols:    The names of all output fields (i.e. aliases) which are not aggregation
                                expressions are listed here, in the provided [].
        """
        self.s2p = s2p
        self.aggs = aggs
        self.non_agg_cols = non_agg_cols
        self.keep = []
        self.rename = {}
        self.calculations = []
        self.calculations_after = []
        self.agg_exprs = {}
        self.exclude_fields = set()
        self.after_field_map = {}

    def one_field(self, expr, alias, hidden: bool=False, after: bool=False):
        """
        Process one field.
        :param expr:    Expression for field
        :param alias:   Alternate name
        :param hidden:  This is a temporary field which will be removed later.
        """
        if isinstance(expr, Node_Field) and not hidden:
            return self._one_field_simple(expr, alias)
        calc_name = alias or str(expr)
        if aggregate_exprs(expr, self.agg_exprs):
            self.aggs.append((calc_name, expr))
        else:
            lhs = "%s[%s]" % (self.s2p.tmpvar, repr(calc_name))
            if after:
                self.calculations_after.append(self.s2p.render_calc(lhs, expr, field_map=self.after_field_map))
            else:
                self.calculations.append(self.s2p.render_calc(lhs, expr))
            self.s2p.columns_modified = True
            if calc_name not in self.keep and not after:
                self.keep.append(calc_name)
                if not hidden:
                    self.non_agg_cols.append(calc_name)

    def _one_field_simple(self, expr: Node_Field, alias):
        """
        Process the simplest case, where there is no calculation, only the selection of a named
        field, i.e. "SELECT field FROM table".
        :param expr:        The expression, i.e. which field is being selected.
        :param alias:       The alternate name selected for the field, if any.
        """
        field_name = expr.fieldName[-1]
        if field_name.startswith("*["):
            # "SELECT *[removed1, removed2]" is an extension to SQL that lets us exclude some fields without
            # having to know what fields are available.
            # TODO add routine for this in analysis or SqlUtil
            self.exclude_fields = set(map(lambda f: f.strip(), field_name[2:].strip("]").split(",")))
            return
        # indicate this is not a temporary field
        self.keep.append(field_name or alias)
        # indicate this is a non-aggregation field
        self.non_agg_cols.append(alias or field_name)
        # if renaming is taking place, make a note of that
        if alias and field_name != alias:
            self.rename[field_name] = alias

    def build(self, field_list, temp_exprs, temp_exprs_after):
        for expr, alias in field_list:
            self.one_field(expr, alias)
        for expr, alias in (temp_exprs or []):
            self.one_field(expr, alias, hidden=True)
        for expr, alias in (temp_exprs_after or []):
            self.one_field(expr, alias, hidden=True, after=True)
        # save off arguments for all aggregation function calls
        for agg_var, agg_expr in self.agg_exprs.items():
            if agg_var == "*":
                self.keep.append("*")
                continue
            agg_col = str_to_var_name("_agg_" + agg_var)
            lhs = "%s[%s]" % (self.s2p.tmpvar, repr(agg_col))
            self.calculations.append(self.s2p.render_calc(lhs, agg_expr))
            self.keep.append(agg_col)
            self.s2p.columns_modified = True
        code = ""
        if self.calculations:
            code += "\n" + "".join(self.calculations) + "%s = %s" % (self.s2p.tmpvar, self.s2p.tmpvar)
        if self.exclude_fields:
            code += "[list(sorted((set(%s.columns) - %s) | set(%s)))]" % (
                self.s2p.tmpvar, repr(self.exclude_fields), repr(self.keep))
        elif "*" not in self.keep:
            code += "[%s]" % repr(self.keep)
        if self.rename:
            code += ".rename(columns=%s)" % repr(self.rename)
        if self.calculations_after:
            code += "\n" + "".join(self.calculations_after) + "%s = %s" % (self.s2p.tmpvar, self.s2p.tmpvar)
        return code


class NeedToBifurcate(Exception):
    """
    This exception is raised when code needs to be different between pandas and dask.
    """


class NeedToUseCalc(Exception):
    """
    This indicates we can't use pandas.query() and have to use 'calc'-like expressions.  That is...
    """


class CantUseNumExpr(Exception):
    """
    This indicates we can't use query.numexpr(), and have to use the 'python' engine instead.
    """


def _to_pandas(df):
    import pandas
    if isinstance(df, pandas.DataFrame):
        return df
    return df.compute()


# These functions can be run like so:
#    dataframe['column'].abs()
# This is a mapping from the standard SQL function to the qualified function name within pandas/dask.
NATIVE_FUNCTIONS = {
    # string
    "concat": "str.cat",
    "length": "str.len", "len": "str.len", "char_length": "str.len",
    "lcase": "str.lower", "lower": "str.lower", "ucase": "str.upper", "upper": "str.upper",
    "trim": "str.strip", "ltrim": "str.lstrip", "rtrim": "str.rstrip",
    "replace": "str.replace", "substr": "str.slice", "substring": "str.slice",
    # numeric
    "abs": "abs",
    # datetime
    "strftime": "dt.strftime"
}


# these are functions which can be accessed using properties of Series
NATIVE_PROPERTIES = {
    "year": "dt.year", "month": "dt.month", "day": "dt.day"
}


# These functions come from either numpy or dask.array.
NUMPY_FUNCTIONS = {
    # numeric
    'acos': 'arccos', 'asin': 'arcsin', 'atan': 'arctan', 'atan2': 'arctan2', 'ceil': 'ceil', 'ceiling': 'ceil',
    'cos': 'cos', 'degrees': 'degrees', 'exp': 'exp', 'floor': 'floor', 'ln': 'log', 'log': 'log', 'log10': 'log10',
    'log2': 'log2', 'mod': 'mod', 'pi': 'pi', 'pow': 'power', 'power': 'power', 'radians': 'radians', 'rand': 'random',
    'round': 'round', 'sign': 'sign', 'sin': 'sin', 'sqrt': 'sqrt', 'tan': 'tan', 'truncate': 'truncate',
    # other
    'if': 'where'
}


QUERY_FUNCTIONS = {
    "sin": "sin", "cos": "cos", "tan": "tan",
    "asin": "arcsin", "acos": "arccos", "atan": "arctan", "atan2": "arctan2",
    "log": "log", "log10": "log10", "exp": "exp",
    "sqrt": "sqrt", "abs": "abs",
}


QUERY_SUB_FUNCTIONS = NATIVE_FUNCTIONS


SQL_TYPES_TO_PANDAS_TYPES = {"datetime": "datetime64"}
