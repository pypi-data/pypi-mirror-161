import functools

from .compiled import _cmp, Node_Field, Node_Op, SqlOrderBy
from .data import SqlTableStream, SqlFieldInfo
from .eval_utils import find_field_in_list, SqlEvaluationContext


class Union(SqlTableStream):
    def __init__(self, streams):
        SqlTableStream.__init__(self, streams)
        self.fields = None
        self.fieldMap = {}
        self.streams = streams

    def _calcFields(self):
        # align the fields
        new_fields = []
        for stream in self.streams:
            for field in stream.getFields():
                key = (field.alias or field.field).lower()
                if key not in self.fieldMap:
                    self.fieldMap[key] = len(new_fields)
                    new_fields.append(SqlFieldInfo(field=field.field, alias=field.alias))
        self.fields = new_fields

    def getFields(self):
        if self.fields is None:
            self._calcFields()
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        self.getFields()
        for stream in self.streams:
            for row in stream.getRowIterator():
                new_row = [None, ] * len(self.fields)
                for n, field in enumerate(stream.getFields()):
                    key = (field.alias or field.field).lower()
                    idx = self.fieldMap[key]
                    new_row[idx] = row[n]
                if self.context.debugLevel:
                    print("union: out={0}".format(new_row))
                yield tuple(new_row)

    def canLimit(self, start, count):
        if start or count >= 0:
            return False
        return True

    def canWhere(self, where):
        if where:
            return False
        return True

    def canSort(self, sort):
        if sort:
            return False
        return True


class _FieldCalc(SqlTableStream):
    def __init__(
            self, stream, compiler, field_mappings, alias_to_table=None, table_to_alias=None,
            aggregation_grouper=None, downstream_visible_from_upstream=False, upstream_sort=None
    ):
        SqlTableStream.__init__(self, stream)
        self.oldFields = None
        self.fields = None
        self.stream = stream
        self.compiler = compiler
        self.fieldMappings = field_mappings
        self.aliasToTable = alias_to_table
        self.tableToAlias = table_to_alias
        self.aggregationGrouper = aggregation_grouper
        self.downstreamVisibleFromUpstream = downstream_visible_from_upstream
        self.upstream_sort = upstream_sort
        self.stream_cache = {}

    def _gen_stream_field_ref(self, field, alias):
        """
        Generate a reference to a field in 'stream'.
        """
        table_alias = None
        if self.tableToAlias:
            table_alias = self.tableToAlias.get((field.table,)) \
                          or self.tableToAlias.get((field.database, field.table))
        return SqlFieldInfo(
            table=field.table, field=field.field,
            database=field.database, alias=alias or field.alias,
            table_alias=table_alias
        )

    def _calcFields(self):
        self.oldFields = self.stream.getFields()
        # generate new field list
        new_fields = []
        for n, fm in enumerate(self.fieldMappings):
            expr = fm[0]
            alias = fm[1]
            if isinstance(expr, Node_Field):
                i_old = find_field_in_list(expr.fieldName, self.stream.context)
                if i_old != -1:
                    # found field in 'stream' by name
                    new_field = self._gen_stream_field_ref(self.oldFields[i_old], alias)
                elif alias:
                    # field not found - we'll just use the alias
                    new_field = SqlFieldInfo(table=None, field=None, alias=alias)
                elif isinstance(expr.fieldName, tuple) and len(expr.fieldName) >= 2:
                    # field not found - we'll use the given field name as an alias
                    new_field = SqlFieldInfo(table=expr.fieldName[0], field=None,
                                                    alias=expr.fieldName[-1])
                else:
                    # list the alias, without any real table/field information
                    new_field = SqlFieldInfo(table=None, field=None, alias=expr.fieldName[-1])
            else:
                # calculated field
                new_field = SqlFieldInfo(table=None, field=str(expr), alias=alias)
            new_fields.append(new_field)
        return new_fields

    def supplyContext(self, context):
        if self.aliasToTable:
            context = context.derive(tableAliases=self.aliasToTable)
        SqlTableStream.supplyContext(self, context)

    def getFields(self):
        if self.fields is None:
            self.fields = self._calcFields()
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        self.getFields()
        if self.aggregationGrouper and not self.stream.canSort(self.upstream_sort):
            i = _FieldCalcRowIter(self, where)
            for row in i.scan_aggregate_upstream_unsorted():
                yield row
        else:
            i = _FieldCalcRowIter(self, where, sort=self.upstream_sort)
            for row in i.scan(sort=sort, start=start, count=count):
                yield row

    def _clone_fieldMappings(self):
        from copy import deepcopy
        return deepcopy(self.fieldMappings)

    def _eval_row(self, upstream_row, aggregate=True, fieldMappings=None):
        fieldMappings = fieldMappings or self.fieldMappings
        row_to_build = [None] * len(self.fieldMappings)
        ctx1 = self.context.derive(fields=self.getFields(), record=row_to_build, aggregate=aggregate)
        ctx2 = ctx1.derive(fields=self.oldFields, record=upstream_row, cache=self.stream_cache)
        for n, fm in enumerate(fieldMappings):
            row_to_build[n] = fm[0].eval(ctx2)
        return tuple(row_to_build)

    def canSort(self, sort):
        if self.aggregationGrouper:
            if not sort or sort == self.upstream_sort:
                return True
            return False
        return super(_FieldCalc, self).canSort(sort)

    def canWhere(self, where):
        return True

    def canLimit(self, start, count):
        if self.aggregationGrouper:
            return False
        return super(_FieldCalc, self).canLimit(start, count)


class _FieldCalcRowIter(object):
    def __init__(self, calc, where=None, sort=None):
        self.calc = calc
        calc.getFields()
        self.ctx_downstream = calc.context.derive(fields=calc.getFields())
        if calc.downstreamVisibleFromUpstream:
            self.ctx_upstream = self.ctx_downstream.derive(fields=calc.oldFields)
        else:
            self.ctx_upstream = SqlEvaluationContext(fields=calc.oldFields)
        where_parts = split_expr_by_upstream_availability(
            where, self.ctx_upstream, self.ctx_downstream, prefer_upstream=bool(calc.aggregationGrouper)
        )
        self.where_keep = where_parts[0]
        self.where_upstream = where_parts[1]
        self.apply_sort = sort
        self.use_stream = calc.stream
        if not calc.stream.canWhere(self.where_upstream):
            self.use_stream = calc.compiler.support_where_and_limit(calc.stream)

    def check_where(self, row):
        if not self.where_keep:
            return True
        ok = test_sql_filter(self.where_keep, self.ctx_downstream.derive(record=row))
        if self.ctx_downstream.debugLevel:
            print("calculateOrSelectFields: where={0}, {1}".format(ok, self.where_keep))
        return ok

    def _dbg(self, **kwargs):
        if self.calc.context and self.calc.context.debugLevel:
            print("calculateOrSelectFields: %s" % kwargs)

    def _tail(self, last_group, last_row):
        if self.calc.aggregationGrouper:
            new_row = self.calc._eval_row(last_row, aggregate=False)
            self._dbg(agg=last_group, row_out=new_row)
            if self.check_where(new_row):
                return new_row

    def scan(self, sort=None, start=0, count=-1):
        calc = self.calc
        prev_group = None
        prev_row = None
        for row in self.use_stream.getRowIterator(where=self.where_upstream, sort=self.apply_sort or sort, start=start, count=count):
            ctx = self.ctx_upstream.derive(record=row)
            if not calc.aggregationGrouper:
                # non-aggregated row
                new_row = calc._eval_row(row)
                self._dbg(row_in=row, row_out=new_row)
                if self.check_where(new_row):
                    yield new_row
                continue
            # determine grouping
            current_group = calc.aggregationGrouper(ctx)
            if prev_group and current_group != prev_group:
                # group changed
                new_row = calc._eval_row(prev_row, aggregate=False)
                self._dbg(agg=current_group, row_out=new_row)
                if self.check_where(new_row):
                    yield new_row
            prev_group = current_group
            # aggregate to current group
            self._dbg(agg=current_group, row_in=row)
            calc._eval_row(row)
            prev_row = row
        out = self._tail(prev_group, prev_row)
        if out:
            yield out

    def scan_aggregate_upstream_unsorted(self):
        """
        Aggregation that doesn't require upstream sorting.
        """
        calc = self.calc
        groups = {}
        for row in self.use_stream.getRowIterator(where=self.where_upstream):
            ctx = self.ctx_upstream.derive(record=row)
            current_group = calc.aggregationGrouper(ctx)
            group = groups.get(current_group)
            if group:
                group_fm = group[0]
            else:
                group_fm = calc._clone_fieldMappings()
                groups[current_group] = (group_fm, row)
            calc._eval_row(row, fieldMappings=group_fm)
        for _, (group_fm, group_row) in sorted(groups.items()):
            row = calc._eval_row(group_row, fieldMappings=group_fm, aggregate=False)
            if self.check_where(row):
                yield row


class _JoinMerger(SqlTableStream):
    def __init__(self, stream_l, stream_r, join_type, join_expr, compiler):
        super(_JoinMerger, self).__init__([stream_l, stream_r])
        self.streamL = stream_l
        self.streamR = stream_r
        self.joinType = join_type
        self.joinExpr = join_expr
        self.compiler = compiler
        self.fields = None
        self.leftJoin = "left" in join_type
        self.rightJoin = "right" in join_type
        self.innerJoin = "inner" in join_type
        self.fullJoin = "full" in join_type or "outer" in join_type
        if not self.leftJoin and not self.rightJoin and not self.innerJoin and not self.fullJoin:
            self.innerJoin = True

    def supplyContext(self, context):
        SqlTableStream.supplyContext(self, context)
        if context:
            self.context = context.derive(fields=self.getFields())

    def getFields(self):
        if self.fields is None:
            self.fields = self.streamL.getFields() + self.streamR.getFields()
        return self.fields

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        expr_parts = analyze_expr_for_join(where_and_where(where, self.joinExpr), self.streamL.context, self.streamR.context)
        s_l, s_r = self._prepare_streams(expr_parts)
        i = _JoinMergerIterator(expr_parts, self, s_l, s_r)
        for row in i.iterate():
            if i.post_filter(row):
                yield row

    def _prepare_streams(self, expr_parts):
        s_l = self.streamL
        s_r = self.streamR
        compiler = self.compiler
        assert s_l.context and s_r.context
        #print("analyze_expr_for_join: {0}".format(where_and_where(where, self.joinExpr)))
        #print("leftExprs={0}, rightExprs={1}, leftOnly={2}, rightOnly={3}".format([str(x) for x in expr_parts.leftExprs], [str(x) for x in expr_parts.rightExprs], expr_parts.leftOnly, expr_parts.rightOnly))
        # pre-filter the parts of the expression that relate to the source streams
        if expr_parts.left_only:
            s_l = compiler.apply_where(s_l, expr_parts.left_only)
        if expr_parts.right_only:
            s_r = compiler.apply_where(s_r, expr_parts.right_only)
        assert s_l.context and s_r.context
        # apply sorting to incoming streams
        if expr_parts.left_exprs:
            order = SqlOrderBy()
            for var in expr_parts.left_exprs:
                order.addLevel(var)
            s_l = compiler.apply_sort(s_l, order)
            order = SqlOrderBy()
            for var in expr_parts.right_exprs:
                order.addLevel(var)
            s_r = compiler.apply_sort(s_r, order)
        return s_l, s_r

    def canLimit(self, start, count):
        if start or count >= 0:
            return False
        return True

    def canWhere(self, where):
        return True

    def canSort(self, sort):
        return not sort


class _JoinMergerIterator(object):
    def __init__(self, expr_parts, joiner, stream_l, stream_r):
        self.expr_parts = expr_parts
        self.joiner = joiner
        self.context = joiner.context
        self.stream_l = stream_l
        self.stream_r = stream_r
        self.fields_l = stream_l.getFields()
        self.fields_r = stream_r.getFields()
        self.null_l = (None,) * len(self.fields_l)
        self.null_r = (None,) * len(self.fields_r)
        self.i_l = iter(self.stream_l.getRowIterator())
        self.i_r = iter(self.stream_r.getRowIterator())
        self.r_l = _nxt(self.i_l)
        self.r_r = _nxt(self.i_r)

    def post_filter(self, r):
        if self.expr_parts.other:
            ok = test_sql_filter(self.expr_parts.other, self.context.derive(record=r))
            if self.context.debugLevel:
                print("join: postFilter={0}, pass={1}".format(self.expr_parts.other, ok))
            if not ok:
                return False
        if self.context.debugLevel:
            print("join: emit={0}".format(r))
        return True

    def compare(self, r_l, r_r):
        c = 0
        for n, x_l in enumerate(self.expr_parts.left_exprs):
            x_r = self.expr_parts.right_exprs[n]
            v_l = x_l.eval(self.context.derive(record=r_l, fields=self.fields_l)) if r_l else None
            v_r = x_r.eval(self.context.derive(record=r_r, fields=self.fields_r)) if r_r else None
            c = _cmp(v_l, v_r)
            if c:
                break
        return c

    def _iter_dbg(self, match):
        if self.context.debugLevel:
            print("join {0}, L={1}, R={2}, match={3}".format(self.joiner.joinType, self.r_l, self.r_r, match))

    def iterate(self):
        while self.r_l and self.r_r:
            match = self.compare(self.r_l, self.r_r)
            self._iter_dbg(match)
            for out in self._cycle(match):
                yield out
        # one of the streams has ended
        for out in self._tail():
            yield out

    def _cycle(self, match):
        # let the recessive stream catch up
        if self.joiner.leftJoin:
            if match > 0:
                # skip right
                self.r_r = _nxt(self.i_r)
                return
            elif match < 0:
                # emit left only
                out = self.r_l + self.null_r
                yield out
                self.r_l = _nxt(self.i_l)
                return
        if self.joiner.rightJoin:
            if match < 0:
                self.r_l = _nxt(self.i_l)
                return
            elif match > 0:
                # emit right only
                out = self.null_l + self.r_r
                yield out
                self.r_r = _nxt(self.i_r)
                return
        if self.joiner.innerJoin:
            if match < 0:
                self.r_l = _nxt(self.i_l)
                return
            elif match > 0:
                self.r_r = _nxt(self.i_r)
                return
        # we must be in full join mode if match!=0 at this point
        if match < 0:
            out = self.r_l + self.null_r
            yield out
            self.r_l = _nxt(self.i_l)
            return
        elif match > 0:
            out = self.null_l + self.r_r
            yield out
            self.r_r = _nxt(self.i_r)
            return
        # merge
        # - gather all matching instances on left and right
        for out in self._gather_leftovers(match):
            yield out

    def _tail(self):
        # one of the streams has ended
        if self.joiner.innerJoin:
            return
        if not self.joiner.rightJoin:
            while self.r_l:
                out = self.r_l + self.null_r
                yield out
                self.r_l = _nxt(self.i_l)
        if not self.joiner.leftJoin:
            while self.r_r:
                out = self.null_l + self.r_r
                yield out
                self.r_r = _nxt(self.i_r)

    def _gather_leftovers(self, match):
        # cross-join for multiple matching rows
        all_l = [self.r_l]
        all_r = [self.r_r]
        while match == 0:
            self.r_l = _nxt(self.i_l)
            if not self.r_l:
                break
            match = self.compare(self.r_l, self.r_r)
            if match == 0:
                all_l.append(self.r_l)
        match = 0
        while match == 0:
            self.r_r = _nxt(self.i_r)
            if not self.r_r:
                break
            match = self.compare(all_l[0], self.r_r)
            if match == 0:
                all_r.append(self.r_r)
        # yield all combinations of all_l and all_r
        for o_l in all_l:
            for o_r in all_r:
                out = o_l + o_r
                yield out


class _UpstreamAvailabilitySplitter(object):
    DOWN = 0
    UP = 1

    def __init__(self, upstream_context, downstream_context, prefer_upstream=False):
        self.upstream_context = upstream_context
        self.downstream_context = downstream_context
        self.prefer_upstream = prefer_upstream
        self.split_out = [None, None]

    def send_node(self, cat, node):
        if self.split_out[cat] is None:
            self.split_out[cat] = node
        else:
            self.split_out[cat] = Node_Op("and", [self.split_out[cat], node])

    def analyze_group(self, node):
        if self.keep_downstream(node):
            self.send_node(self.DOWN, node)
        else:
            self.send_node(self.UP, node)

    def can_go_up(self, node):
        if isinstance(node, Node_Field):
            return self.upstream_context.namedValueAvailable(node.fieldName)
        if hasattr(node, "children") and not all(map(self.can_go_up, node.children)):
            return False
        return True

    def can_go_down(self, node):
        if isinstance(node, Node_Field):
            return self.downstream_context.namedValueAvailable(node.fieldName)
        if hasattr(node, "children") and not all(map(self.can_go_down, node.children)):
            return False
        return True

    def keep_downstream(self, node):
        if self.can_go_up(node):
            return False
        if self.can_go_down(node):
            return True
        if self.prefer_upstream:
            return False
        return True

    def split(self, expr):
        if expr:
            for sub in top_level_ands(expr):
                self.analyze_group(sub)
        return self.split_out


def split_expr_by_upstream_availability(expr, upstream_context, downstream_context, prefer_upstream=False):
    """
    Split an expression into two sets of components to be evaluated by different
    levels of a compiled stream.  Any components that only reference fields in the
    upstreamContext will be put into the second category, and all others go into the first.

    :return:  A list with two elements: the downstream and the local.
    """
    return _UpstreamAvailabilitySplitter(upstream_context, downstream_context, prefer_upstream).split(expr)


def test_sql_filter(where, ctx):
    """
    Evaluate a WHERE expression against a given row
    """
    if not where:
        return True
    v = where.eval(ctx)
    return bool(v)


def where_and_where(where1, where2):
    """
    Combine two where expressions with an AND.
    """
    if not where1 and not where2:
        return None
    if where1 and not where2:
        return where1
    if where2 and not where1:
        return where2
    return Node_Op("and", [where1, where2])


class _JoinAnalyzer(object):
    def __init__(self, left_context, right_context):
        self.out = _JoinParts()
        self.left_context = left_context
        self.right_context = right_context

    def _categorize_field(self, field_name):
        if find_field_in_list(field_name, self.left_context) != -1:
            return "L"
        if find_field_in_list(field_name, self.right_context) != -1:
            return "R"
        return "LR"

    def categorize(self, node):
        if isinstance(node, Node_Field):
            return self._categorize_field(node.fieldName)
        if hasattr(node, "children"):
            t = None
            for child in node.children:
                sub = self.categorize(child)
                if sub:
                    t = sub if (t == sub or t is None) else "LR"
            return t

    def analyze_group(self, node):
        {
            "L": self.out.addLeft,
            "R": self.out.addRight,
            "LR": self.analyze_lr,
            None: self.out.addOther
        }[self.categorize(node)](node)

    def analyze_lr(self, node):
        if not isinstance(node, Node_Op) or node.operator not in {"=", "=="}:
            self.out.addOther(node)
            return
        c_l = self.categorize(node.children[0])
        c_r = self.categorize(node.children[1])
        if c_l == "L" and c_r == "R":
            self.out.left_exprs.append(node.children[0])
            self.out.right_exprs.append(node.children[1])
        elif c_l == "R" and c_r == "L":
            self.out.right_exprs.append(node.children[0])
            self.out.left_exprs.append(node.children[1])
        else:
            self.out.addOther(node)

    def analyze(self, expr):
        for sub in top_level_ands(expr):
            self.analyze_group(sub)
        return self.out


def analyze_expr_for_join(expr, left_context, right_context):
    # TODO <R.field is NONE> does not make sense as a pre-filter because missing fields come through as None
    return _JoinAnalyzer(left_context, right_context).analyze(expr)


class _JoinParts(object):
    """
    leftExprs, rightExprs: aligned lists of expressions that can be used to qualify a join
    leftOnly, rightOnly: expressions that apply only to the left or right table
    other: the part of the expression that can only be used to post-qualify the join
    """

    def __init__(self):
        self.left_exprs = []
        self.right_exprs = []
        self.left_only = None
        self.right_only = None
        self.other = None

    def addLeft(self, node):
        if self.left_only:
            self.left_only = Node_Op("and", [self.left_only, node])
        else:
            self.left_only = node

    def addRight(self, node):
        if self.right_only:
            self.right_only = Node_Op("and", [self.right_only, node])
        else:
            self.right_only = node

    def addOther(self, node):
        if self.other:
            self.other = Node_Op("and", [self.other, node])
        else:
            self.other = node


def _nxt(i):
    try:
        return i.__next__()
    except StopIteration:
        return None


def top_level_ands(node):
    """
    Generate an iteration over all of the ANDs in an expression that precede all other parts, i.e.:
        a AND b  ==>  (a, b)
        a AND (b or c) ==>  (a, (b or c))
        a * 2 ==> ()
    """
    if isinstance(node, Node_Op) and node.operator == "and":
        for sub in node.children:
            for s2 in top_level_ands(sub):
                yield s2
    else:
        yield node


class SortableStream(SqlTableStream):
    """
    Add sorting capability to a stream.
    """
    def __init__(self, stream):
        SqlTableStream.__init__(self, stream)

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        if self.upstream.canSort(sort):
            # let upstream do its own sorting if it is able
            out = self.upstream.getRowIterator(where, sort, start, count)
            # if upstream can sort but can't limit, we have to apply the limit here as well
            if not self.upstream.canLimit(start, count):
                # TODO optimize this for large streams
                out = list(out)
                if count:
                    out = out[start:start+count]
                elif start:
                    out = out[start:]
            return out
        else:
            ctx = self.upstream.context.derive(fields=self.getFields())
            if count >= 0:
                # there is a limit we can apply
                upstream_rows = self.upstream.getRowIterator(where)
                rows = top_sort(upstream_rows, sort=sort, limit=start + count, context=ctx)
                if start:
                    rows = rows[start:]
            else:
                # we have to sort the entire data set
                upstream_rows = self.upstream.getRowIterator(where, None, start, count)
                rows = list(upstream_rows)
                def sort_cmp(a, b):
                    return sort.compare(a, b, ctx)
                rows.sort(key=functools.cmp_to_key(sort_cmp))
                if count >= 0:
                    rows = rows[start:start+count]
                elif start:
                    rows = rows[start:]
            return rows

    def canSort(self, sort):
        return True

    def canLimit(self, start, count):
        return True


class TopList(object):
    def __init__(self, cmp, limit):
        self.cmp = cmp
        self.limit = limit
        self.data = []

    def locate(self, value):
        if not self.data:
            return 0
        lo = 0
        hi = len(self.data)
        while lo < hi:
            mid = (lo + hi) // 2
            cmp = self.cmp(value, self.data[mid])
            if cmp == 0:
                return mid
            if cmp > 0:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def add(self, value):
        ins_before = self.locate(value)
        self.data.insert(ins_before, value)
        if len(self.data) > self.limit:
            self.data = self.data[:self.limit]


def top_sort(upstream, sort, limit, context):
    def sort_cmp(a, b):
        return sort.compare(a, b, context)
    top = TopList(cmp=sort_cmp, limit=limit)
    for row in upstream:
        top.add(row)
    return top.data


class WhereAndLimit(SqlTableStream):
    """
    Adds filtering and range capabilities.
    """
    def __init__(self, stream, force_post_filter):
        SqlTableStream.__init__(self, stream)
        self.force_post_filter = force_post_filter

    def getRowIterator(self, where=None, sort=None, start=0, count=-1):
        limit_upstream = (0, -1)
        where_upstream = None
        if self.upstream.canLimit(start, count):
            limit_upstream = (start, count)
            start, count = 0, -1
        if not self.force_post_filter and self.upstream.canWhere(where):
            where_upstream = where
            where = None
        base_ctx = self.context.derive(fields=self.getFields())
        for row in self.upstream.getRowIterator(where_upstream, sort, limit_upstream[0], limit_upstream[1]):
            ok = test_sql_filter(where, base_ctx.derive(record=row))
            if self.context.debugLevel:
                print("where: {0}, {1}".format(ok, where))
            if not ok:
                continue
            if start:
                start -= 1
                continue
            if count == 0:
                break
            if count > 0:
                count -= 1
            yield row

    def canWhere(self, where):
        return True

    def canLimit(self, start, count):
        return True
