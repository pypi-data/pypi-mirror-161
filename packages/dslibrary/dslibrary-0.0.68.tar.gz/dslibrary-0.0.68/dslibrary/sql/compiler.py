from .compiled import uses_aggregation, Node_Field, SqlOrderBy
from .data import SqlTableStream, MemoryDataSupplier, SqlFieldInfo
from .eval_utils import find_field_in_list
from .exceptions import SqlException, SqlException_DataSourceNotFound
from .parser import expand_field_spec
from .select_stmt import SqlSelect
from .streams import _JoinMerger, where_and_where, test_sql_filter, _FieldCalc, Union, WhereAndLimit, SortableStream


class SqlCompiler(object):
    """
    Through an instance of this class, a parser can generate any kind of data stream, i.e. an instance of
    SqlTableStream that performs all sorts of joining, aggregation, filtering, sorting and so on.
    """

    def data_source(self, table_spec):
        assert isinstance(table_spec, tuple)
        """
        Get the lowest level of data stream.  Data will be pulled from one of the
        data suppliers provided by the context.
        """

        class DataSource(SqlTableStream):
            def __init__(self):
                super(DataSource, self).__init__()
                self.source = None

            def supplyContext(self, context):
                self.source = context.findDataSource(table_spec)
                if not self.source:
                    raise SqlException_DataSourceNotFound("not found: {0}".format(".".join(table_spec)))
                self.source.supplyContext(context)
                self.context = context.derive(fields=self.getFields())
                self.upstream = self.source

            def getFields(self):
                return self.source.getFields()

            def getRowIterator(self, where=None, sort=None, start=0, count=-1):
                return self.source.getRowIterator(where, sort, start, count)

            def canSort(self, sort):
                return self.source.canSort(sort)

            def canWhere(self, where):
                return self.source.canWhere(where)

            def canLimit(self, start, count):
                return self.source.canLimit(start, count)

        return DataSource()

    def distinctify(self, stream, fields=None):
        """
        Filter out duplicate values from a stream.
        :param stream:   Stream to apply to.
        :param fields:   List of field specifiers - an iterable of strings or tuples.
        :return:    New stream.
        """

        class Distinct(SqlTableStream):
            def __init__(self):
                SqlTableStream.__init__(self, stream)

            def getRowIterator(self, where=None, sort=None, start=0, count=-1):
                distinct = set()
                ctx = self.context.derive(fields=self.getFields())

                def value_to_make_distinct(row):
                    if not fields:
                        return row
                    out = []
                    for f in fields:
                        idx = find_field_in_list(f, ctx)
                        if idx != -1:
                            out.append(row[idx])
                    return tuple(out)

                for row in stream.getRowIterator(where, sort, start, count):
                    v = value_to_make_distinct(row)
                    if v not in distinct:
                        distinct.add(v)
                        yield row

        return Distinct()

    def join(self, stream_l, stream_r, join_type, join_expr):
        """
        Merge two streams into one.
        :param stream_l:
        :param stream_r:
        :param join_type:
        :param join_expr:
        :return:
        """
        return _JoinMerger(stream_l, stream_r, join_type=join_type, join_expr=join_expr, compiler=self)

    def support_where_and_limit(self, stream, force_post_filter=False):
        """
        Add filtering capability to a stream.
        """
        out = WhereAndLimit(stream, force_post_filter)
        if stream.context:
            out.supplyContext(stream.context)
        return out

    def support_sort(self, stream):
        """
        Add sorting support to a stream.
        """
        return SortableStream(stream)

    def apply_where(self, stream, where_condition, force_post_filter=False):
        """
        Filter a stream.
        """
        class Where(SqlTableStream):
            def __init__(self):
                SqlTableStream.__init__(self, stream)
                if stream.context:
                    self.supplyContext(stream.context)

            def getRowIterator(self, where=None, sort=None, start=0, count=-1):
                combined_where = where_and_where(where, where_condition)
                if not force_post_filter and stream.canWhere(combined_where):
                    return stream.getRowIterator(combined_where, sort, start, count)

                def gen():
                    ctx0 = self.context.derive(fields=self.getFields())
                    for row in stream.getRowIterator(None, sort, start, count):
                        ctx = ctx0.derive(record=row)
                        if test_sql_filter(combined_where, ctx):
                            yield row

                return gen()

        return Where()

    def apply_sort(self, stream, sort_spec):
        """
        Sort a stream.
        """
        cmp = self

        class Sort(SqlTableStream):
            def __init__(self):
                SqlTableStream.__init__(self, stream)
                if stream.context:
                    self.supplyContext(stream.context)

            def getRowIterator(self, where=None, sort=None, start=0, count=-1):
                combined_sort = sort or sort_spec
                if stream.canSort(combined_sort):
                    return stream.getRowIterator(where, combined_sort, start, count)
                return cmp.get_full_row_iterator(stream, where, combined_sort, start, count)

            def canSort(self, sort):
                return True

            def canLimit(self, start, count):
                return True

        return Sort()

    def apply_limit(self, stream, apply_start=0, apply_count=-1):
        """
        Apply limits to a stream.
        """
        cmp = self

        class Limits(SqlTableStream):
            def __init__(self):
                SqlTableStream.__init__(self, stream)

            def getRowIterator(self, where=None, sort=None, start=0, count=-1):
                limits = combine_limits((apply_start, apply_count), (start, count))
                return cmp.get_full_row_iterator(stream, where, sort, limits[0], limits[1])

            def canLimit(self, start, count):
                return True

        return Limits()

    def get_full_row_iterator(self, stream, where=None, sort=None, start=0, count=-1):
        """
        Fills in whatever capabilities a stream is missing.
        """
        full = stream
        if (where and not full.canWhere(where)) or ((start or count >= 0) and not full.canLimit(start, count)):
            assert stream.context
            full = self.support_where_and_limit(full)
            full.supplyContext(stream.context)
        if sort and not full.canSort(sort):
            assert stream.context
            full = self.support_sort(full)
            full.supplyContext(stream.context)
        return full.getRowIterator(where, sort, start, count)

    def calculate_or_select_fields(self, stream, field_mappings, **kwargs):
        """
        Modify the list of fields in a stream.  Each entry in fieldMappings is a tuple with the following:
          [0]: the expression to evaluate
          [1]: the new alias to give the field, if any
        """
        # create the stream that modifies fields
        return _FieldCalc(stream, compiler=self, field_mappings=field_mappings, **kwargs)

    def generate_aggregation_grouper(self, group_by):
        """
        Perform aggregation.  The supplied 'aggregationSpec' is an iterable with either a SqlAggregator
        instance or None for each field position.
        """
        def grouper(context):
            if not group_by:
                return 0
            return tuple(level[0].eval(context) for level in group_by.levels)
        return grouper

    def union(self, streams):
        """
        Concatenate streams.
        """
        return Union(streams)

    def add_table_alias(self, stream, new_alias):
        """
        Adds a table alias to a stream.
        """
        return AliasAdder(stream, new_alias)

    def compile_select(self, select, context=None, subquery=False):
        """
        Generate a table stream, given a parsed select statement.

        :param select:  an instance of SqlSelect, i.e. from SqlParser.parseSelect()
        :param context: an instance of SqlUtil.SqlEvaluationContext()
        :param subquery: hint: this is a subquery
        """
        assert isinstance(select, SqlSelect)

        def find_table(from_expr):
            if from_expr.subquery:
                s = self.compile_select(from_expr.subquery, context)
            else:
                s = self.data_source(from_expr.table)
            if from_expr.alias:
                s = self.add_table_alias(s, from_expr.alias)
            return s

        # generate stream using FROM expression
        if not select.from_expr:
            stream = self._compile_select__single_row(select, context)
        else:
            stream = self._compile_select__composite_from(select, subquery, find_table, context)
        # qualify with WHERE, etc.
        stream = self._compile_select__qualify(select, stream, context)
        # result is 'stream'
        if context:
            stream.supplyContext(context)
        return stream

    def _value_or_eval(self, spec, context, default):
        if spec is None:
            return default
        return spec.eval(context)

    def _compile_select__qualify(self, select, stream, context):
        # WHERE
        if select.where:
            stream = self.apply_where(stream, select.where)
        # HAVING
        if select.having:
            stream = self.apply_where(stream, select.having, force_post_filter=True)
        # ORDER BY
        if select.order_by:
            stream = self.apply_sort(stream, select.order_by)
        # START/LIMIT
        start = self._value_or_eval(select.start, context, 0)
        limit = self._value_or_eval(select.limit, context, -1)
        if start or limit not in {0, -1}:
            stream = self.apply_limit(stream, start, limit or -1)
        # UNION
        if select.union:
            to_union = [stream] + [self.compile_select(sel, context) for sel in select.union]
            stream = self.union(to_union)
        # DISTINCT
        if select.distinct is not None:
            stream = self.distinctify(stream, fields=select.distinct or None)
        return stream

    def _compile_select__single_row(self, select, context):
        # single row
        single_row = {}
        for field in select.fields:
            expr, alias = field
            value = expr.eval(context)
            if not alias:
                alias = str(expr)
            single_row[alias] = value
        mem = MemoryDataSupplier(data={"T": [single_row]})
        return mem.getTableStream(("T",))

    def _compile_select__composite_from(self, select, subquery, find_table, context):
        # FROM/JOIN
        alias_to_table = select.getAliasToTableMapping()
        stream = find_table(select.from_expr)
        join = select.from_expr.join
        d_from_u = subquery
        while join:
            tbl = find_table(join)
            stream = self.join(stream, tbl, join.joinType, join.joinExpr)
            join = join.join
        # GROUP BY
        upstream_sort = None
        grouper = None
        if uses_aggregation(select):
            # pre-sort the stream based on the grouping
            if select.group_by:
                upstream_sort = select.group_by
            # generate grouping function to aggregate results
            grouper = self.generate_aggregation_grouper(select.group_by)
            d_from_u = True
        # FIELDS
        if select.isWildcard() and not grouper:
            # no modifications or field calculations or aggregation--don't bother wrapping the stream
            return stream
        field_list = _expand_wildcards(select, alias_to_table, context)
        table_to_alias = {alias_to_table[k]: k for k in alias_to_table}
        return self.calculate_or_select_fields(
            stream, field_list, alias_to_table=alias_to_table,
            table_to_alias=table_to_alias, aggregation_grouper=grouper,
            downstream_visible_from_upstream=d_from_u, upstream_sort=upstream_sort
        )


class AliasAdder(SqlTableStream):
    def __init__(self, upstream, new_alias):
        SqlTableStream.__init__(self, upstream)
        self.fields = []
        self.new_alias = new_alias

    def remove_alias(self, node):
        if isinstance(node, Node_Field):
            field_name = node.fieldName
            if len(field_name) > 1 and field_name[-1] == self.new_alias:
                return Node_Field(field_name[-1:])
            else:
                return node
        elif hasattr(node, "children"):
            new_node = node.clone()
            new_node.children = [self.remove_alias(sub) for sub in node.children]
            return new_node
        else:
            return node

    def supplyContext(self, context):
        SqlTableStream.supplyContext(self, context)
        ff = []
        for f in self.upstream.getFields():
            ff.append(SqlFieldInfo(table=f.table, field=f.field, database=f.database, alias=f.alias,
                                           table_alias=self.new_alias))
        self.fields = ff
        self.context = context.derive(fields=self.fields)

    def getFields(self):
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        # remove the alias from where and sort
        if where:
            where = self.remove_alias(where)
        if sort:
            s2 = SqlOrderBy()
            for lvl in sort.levels:
                s2.addLevel(self.remove_alias(lvl[0]), lvl[1])
            sort = s2
        return self.upstream.getRowIterator(where, sort, start, count)


def combine_limits(limits1, limits2):
    """
    Apply one set of (start, count) to another.

    Limits1 are applied first, then limits2 apply next.
    """
    start = limits1[0]
    count = limits1[1]
    if limits2[0] > 0:
        start2 = limits2[0]
        if count != -1 and start2 > count:
            count = 0
        else:
            start += start2
            if count != -1:
                count -= start2
    if limits2[1] != -1:
        count2 = limits2[1]
        if count2 < count or count == -1:
            count = count2
    return (start, count)


class _WildcardExpander(object):
    def __init__(self, context, table_aliases):
        self.context = context
        self.table_aliases = table_aliases
        self.out = []

    def get_fields_for_table(self, table_spec):
        src = self.context.findDataSource(table_spec)
        if src:
            return [field.field for field in src.getFields()]
        return []

    def add(self, field, expanded):
        expanded = list(expanded)
        if len(expanded) == 1:
            # single field - we can preserve the alias
            if field[-1]:
                self.out.append((Node_Field(expanded[0]), field[1]))
            return
        for f in expanded:
            if f[-1]:
                self.out.append((Node_Field(f), None))

    def find(self, select_spec):
        found_wild = False
        for f in select_spec.fields:
            if not(isinstance(f[0], Node_Field) and f[0].isWildcard()):
                self.out.append(f)
                continue
            if not self.context:
                raise SqlException("no context provided, cannot expand wildcards")
            found_wild = True
            expanded = expand_field_spec(
                select_spec, f[0].fieldName, self.get_fields_for_table, alias_to_table=self.table_aliases
            )
            # custom extension to SQL: a 'non-greedy' wildcard that lets you pull in "all other fields"
            if f[0].fieldName[-1].endswith("?"):
                # the "?" prevents duplicate field names from being selected
                prev_fields = {o[0].fieldName[-1] if isinstance(o[0], Node_Field) else o[1] for o in
                               self.out}
                expanded = filter(lambda x: x[-1] not in prev_fields, expanded)
            # add to results
            self.add(f, expanded)
        if found_wild:
            return self.out
        return select_spec.fields


def _expand_wildcards(select_spec, table_aliases, context):
    """
    Expand "*" and "table.*" references in a field list.
    Returns an expanded field list.
    """
    assert isinstance(select_spec, SqlSelect)
    exp = _WildcardExpander(context, table_aliases)
    return exp.find(select_spec)
