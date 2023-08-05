import time
import re
import math
import unicodedata
from dateutil.parser import parse as parse_date

from .misc import sql_enquote_id, enquote_string_literal, parse_iso_datetime
from .eval_utils import OP_PRECEDENCE, SqlEvaluationContext


ALL_FUNCTIONS = frozenset({
    # GENERAL/LOGICAL
    "typeof", "not", "coalesce", "isnull", "ifnull", "nullif", "if",
    # STRING
    "length", "len",
    "lcase", "lower", "ucase", "upper", "left", "right",
    "concat", "hex",
    "glob", "zeroblob", "randomblob",
    "trim", "char", "chr", "instr", "like", "ltrim", "quote", "replace", "rtrim",
    "regexp_replace", "soundex", "substr", "unicode",
    # MATH
    "abs", "sqrt", "least", "greatest", "round", "floor", "ceil", "ceiling", "random",
    "mod", "pow", "pi", "sin", "cos", "tan", "asin", "acos", "atan", "exp", "log",
    # DATE/TIME
    "strftime", "date", "time", "datetime", "julianday", "now", "year", "month", "day"
})
FUNCTION_ALIASES = {
    "len": "length",
    "ifnull": "isnull",
    "coalesce": "isnull",
    "chr": "char",
    "lcase": "lower",
    "ucase": "upper",
    "ceiling": "ceil",
}
OPERATORS = {
    "||": lambda left, right: str(left) + str(right),
    "=": lambda left, right: left == right,
    "==": lambda left, right: left == right,
    "<": lambda left, right: left < right,
    ">": lambda left, right: left > right,
    "<=": lambda left, right: left <= right,
    ">=": lambda left, right: left >= right,
    "!=": lambda left, right: left != right,
    "<>": lambda left, right: left != right,
    "and": lambda left, right: left and right,
    "or": lambda left, right: left or right,
    "+": lambda left, right: str(left) + str(right) if isinstance(left, str) or isinstance(right, str) else left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
    "/": lambda left, right: left / right if right else None,
    "%": lambda left, right: left % right if right else None,
    "<<": lambda left, right: left << right,
    ">>": lambda left, right: left >> right,
    "&": lambda left, right: left & right,
    "|": lambda left, right: left | right,
    "in": lambda left, right: left in right,
    "not in": lambda left, right: left not in right,
    "like": lambda left, right: _like(left, right),
    "not like": lambda left, right: not _like(left, right),
    "ilike": lambda left, right: _ilike(left, right),
    "not ilike": lambda left, right: not _ilike(left, right),
    "regexp": lambda left, right: re.search(str(right), str(left)) is not None,
    "not regexp": lambda left, right: re.search(str(right), str(left)) is None,
    "match": lambda left, right: re.match("^" + str(right) + "$", str(left)) is not None,
    "not match": lambda left, right: re.match("^" + str(right) + "$", str(left)) is None
}


class EvalContext(object):
    def __init__(self):
        self.current_row = tuple()
        self.current_fields = tuple()


class Node(object):
    def eval(self, ctx):
        return None

    def _cloneOfChildren(self):
        if hasattr(self, "children"):
            return [c.clone() for c in self.children]

    def simplify(self, context):
        if hasattr(self, "children"):
            vals = []
            self.children = [sub.simplify(context) for sub in self.children]
            for sub in self.children:
                if not isinstance(sub, Node_Literal):
                    return self
                vals.append(sub.value)
            return Node_Literal(self.eval(context))
        return self

    def to_sql(self, flavor: str=None):
        return ""

    def __str__(self):
        return self.to_sql()


class Node_Literal(Node):
    def __init__(self, value):
        self.value = value

    def eval(self, ctx):
        return self.value

    def clone(self):
        return Node_Literal(self.value)

    def to_sql(self, flavor: str=None):
        if self.value is None:
            return "NULL"
        if self.value is False:
            return "FALSE"
        if self.value is True:
            return "TRUE"
        if isinstance(self.value, str):
            return enquote_string_literal(self.value)
        else:
            return str(self.value)


class Node_Placeholder(Node):
    def __init__(self):
        """
        A placeholder for a literal value.
        """

    def eval(self, ctx):
        return None

    def clone(self):
        return Node_Placeholder()

    def to_sql(self, flavor: str=None):
        # TODO some day we will have a SQL flavor that uses ? instead of %s
        return "%s"


class Node_Field(Node):
    def __init__(self, field_name, quotes=None):
        """
        A reference to a field.
        :param field_name:  Name of field, as a tuple of strings.  Last one is field name.  Others qualify with
                database, schema, etc..
        :param quotes:      Optional iterable which indicates whether quotes were used for each name component.
        """
        if isinstance(field_name, str):
            field_name = (field_name,)
        self.fieldName = field_name
        self.quotes = quotes

    def isWildcard(self):
        return self.fieldName[-1].startswith("*")

    def getWildcardExceptions(self):
        if self.isWildcard():
            spec = self.fieldName[-1][1:]
            if spec.startswith("["):
                spec = spec[1:]
                if spec.endswith("]"):
                    spec = spec[:-1]
                return spec.split(',')

    def eval(self, ctx):
        if self.isWildcard():
            return 0
        if not ctx:
            raise ValueError(f"Cannot evaluate field='{self.fieldName}' in a literal context")
        return ctx.getNamedValue(self.fieldName)

    def clone(self):
        return Node_Field(self.fieldName, self.quotes)

    def to_sql(self, flavor: str=None):
        quotes = self.quotes or (False,) * len(self.fieldName)
        return ".".join(sql_enquote_id(part, flavor, always) for always, part in zip(quotes, self.fieldName) if part)


class Node_ExtVar(Node):
    """ Reference to an external variable """
    def __init__(self, var_name):
        self.var_name = var_name

    def eval(self, ctx):
        return ctx.getExtVar(self.var_name)

    def clone(self):
        return Node_ExtVar(self.var_name)

    def simplify(self, context):
        return Node_Literal(self.eval(context))

    def to_sql(self, flavor: str=None):
        return "@%s" % sql_enquote_id(self.var_name)


class Functions(object):
    def __init__(self, context):
        self.ctx = context

    def call(self, fn_name, arguments):
        method = "f_%s" % FUNCTION_ALIASES.get(fn_name, fn_name)
        if not hasattr(self, method):
            raise Exception("function not implemented: " + fn_name)
        fn = getattr(self, method)
        args = [arg.eval(self.ctx) for arg in arguments] if arguments else []
        return fn(*args)

    def f_typeof(self, v):
        if v is None:
            return "null"
        if isinstance(v, int):
            return "integer"
        if isinstance(v, float):
            return "real"
        if isinstance(v, str):
            return "text"
        raise Exception("unknown sql type: " + repr(type(v)))

    def f_lower(self, v):
        return str(v).lower()

    def f_upper(self, v):
        return str(v).upper()

    def f_trim(self, v):
        return str(v).strip()

    def f_char(self, v):
        return chr(int(v))

    def f_concat(self, *args):
        return "".join(map(str, args))

    def f_left(self, v1, v2):
        if not v2 or v2 < 0:
            return ""
        return str(v1)[:int(v2)]

    def f_right(self, v1, v2):
        if not v2 or v2 < 0:
            return ""
        return str(v1)[-int(v2):]

    def f_replace(self, v1, v2, v3):
        return str(v1).replace(str(v2), str(v3))

    def f_substr(self, v, start, count=None):
        if start > 0:
            start -= 1
        v = str(v)[start:]
        if count is not None and count < len(v):
            v = v[:count]
        return v

    def f_rtrim(self, v):
        return str(v).rstrip()

    def f_ltrim(self, v):
        return str(v).lstrip()

    def f_instr(self, v1, v2):
        return str(v1).find(v2) + 1

    def f_soundex(self, v):
        return soundex(v)

    def f_not(self, v):
        return not v

    def f_length(self, v):
        return len(str(v))

    def f_abs(self, v):
        return abs(v)

    def f_mod(self, v1, v2):
        if v1 is None:
            return
        if not v2:
            return
        return v1 % v2

    def f_pow(self, v1, v2):
        if v1 is None or v2 is None:
            return
        return v1 ** v2

    def f_pi(self):
        return math.pi

    def f_sin(self, v1):
        return math.sin(v1)

    def f_cos(self, v1):
        return math.cos(v1)

    def f_tan(self, v1):
        return math.tan(v1)

    def f_asin(self, v1):
        return math.asin(v1)

    def f_acos(self, v1):
        return math.acos(v1)

    def f_atan(self, v1):
        return math.atan(v1)

    def f_exp(self, v1):
        return math.exp(v1)

    def f_log(self, v1):
        return math.log(v1)

    def f_if(self, *args):
        cond = args[0]
        t = args[1] if len(args) >= 2 else 1
        f = args[2] if len(args) >= 3 else None
        return t if cond else f

    def f_nullif(self, *args):
        if len(args) < 2:
            return args[0]
        if args[0] == args[1]:
            return None
        return args[0]

    def f_isnull(self, *args):
        v1 = args[0]
        if len(args) < 2:
            return v1
        v2 = args[1]
        return v2 if v1 is None else v1

    def f_sqrt(self, v):
        return math.sqrt(v)

    def f_round(self, v, digits=None):
        if digits is not None:
            return round(v, digits)
        return round(v)

    def f_floor(self, v):
        return math.floor(v)

    def f_ceil(self, v):
        return math.ceil(v)

    def f_least(self, *args):
        return min(args)

    def f_greatest(self, *args):
        return max(args)

    def f_strftime(self, fmt, ts):
        t = _parse_time(ts)
        return time.strftime(fmt, t)

    def f_year(self, ts):
        return _parse_time(ts).tm_year

    def f_month(self, ts):
        return _parse_time(ts).tm_mon

    def f_day(self, ts):
        return _parse_time(ts).tm_mday

    def f_date(self, v1):
        t = _parse_time(v1)
        return time.strftime('%Y-%m-%d', t)

    def f_time(self, v1):
        t = _parse_time(v1)
        return time.strftime('%H:%M:%S', t)

    def f_datetime(self, v1):
        t = _parse_time(v1)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    def f_now(self):
        t = time.gmtime(time.time())
        return time.strftime('%Y-%m-%d %H:%M:%SZ', t)

    def f_julianday(self, v1):
        t = _parse_time(v1)
        return time.mktime(t) / 86400 + 2440587.5

    def f_regexp_replace(self, expr, pattern, replacement):
        return re.sub(pattern, replacement, expr)


class Node_Function(Node):
    def __init__(self, function_name, children=None):
        self.functionName = function_name
        agg = AGGREGATORS.get(function_name)
        if agg:
            self.aggregator = agg()
        else:
            self.aggregator = None
        self.children = children or []

    def isAggregate(self):
        return self.aggregator is not None

    def eval(self, ctx):
        if self.aggregator:
            if not ctx or ctx.aggregate:
                v1 = self.children[0].eval(ctx) if self.children else 0
                self.aggregator.applyValue(v1)
                return 0
            else:
                out = self.aggregator.getResult()
                self.aggregator.reset()
                return out
        '''
           UNSUPPORTED SQLite functions:

           "char", "glob", "hex", "like",
           "quote", "random", "randomblob",
           "unicode", "zeroblob"
        '''
        return Functions(ctx).call(self.functionName, self.children)

    def clone(self):
        return Node_Function(self.functionName, self._cloneOfChildren())

    def to_sql(self, flavor: str=None):
        if self.functionName == "count_distinct":
            return "count(distinct %s)" % ", ".join(sub.to_sql(flavor) for sub in self.children)
        else:
            return "%s(%s)" % (self.functionName, ", ".join(sub.to_sql(flavor) for sub in self.children))


class Node_Unary(Node):
    def __init__(self, child, operator):
        self.children = [child]
        self.operator = operator

    def eval(self, ctx):
        sub = self.children[0].eval(ctx)
        if sub is None:
            return None
        if self.operator == "-":
            if isinstance(sub, (int, float)):
                return -sub
            else:
                raise Exception("'-' applied to non-numeric value")
        if self.operator == "+":
            if isinstance(sub, (int, float)):
                return sub
            else:
                raise Exception("'+' applied to non-numeric value")
        if self.operator == "~":
            if isinstance(sub, (int, float)):
                return ~int(sub)
            else:
                raise Exception("'~' applied to non-numeric value")
        if self.operator == "not":
            return not sub
        raise Exception("operator not implemented: " + self.operator)

    def clone(self):
        return Node_Unary(self.children[0].clone(), self.operator)

    def to_sql(self, flavor: str=None):
        return self.operator + ' ' + self.children[0].to_sql(flavor)


class Node_Cast(Node):
    def __init__(self, child, to_type):
        self.children = [child]
        self.to_type = (to_type or "").lower()

    def eval(self, ctx):
        sub = self.children[0].eval(ctx)
        base_type = self.to_type.split("(")[0]
        if sub is None:
            return None
        if base_type in {"int", "tinyint", "smallint", "bigint", "integer"}:
            try:
                return int(sub)
            except:
                raise Exception("cannot cast %s to int" % type(sub))
        if base_type in {"float", "double", "real"}:
            try:
                return float(sub)
            except:
                raise Exception("cannot cast %s to float" % type(sub))
        if base_type in {"string", "str", "varchar"} or self.to_type.startswith("varchar"):
            try:
                return str(sub)
            except:
                raise Exception("cannot cast %s to str" % type(sub))
        if base_type in {"datetime", "timestamp"}:
            try:
                return parse_iso_datetime(str(sub))
            except:
                raise Exception("cannot cast %s to str" % type(sub))
        raise Exception("type not recognized: " + self.to_type)

    def clone(self):
        return Node_Cast(self.children[0].clone(), self.to_type)

    def to_sql(self, flavor: str=None):
        return "CAST(%s as %s)" % (self.children[0].to_sql(flavor), self.to_type.upper())


class Node_Select(Node):
    def __init__(self, select_spec):
        self.select_spec = select_spec
        self.id = str(select_spec)
        self.cacheable = None

    def getValueList(self, ctx):
        if self.cacheable and self.id in ctx.cache:
            select_result = ctx.cache[self.id]
        else:
            strm = ctx.compiler.compile_select(self.select_spec, ctx.derive(tableAliases={}, aggregate=True),
                                               subquery=True)
            if self.cacheable is None:
                # if any fields are required outside the immediate scope, this implies (or could imply) a query with moving parts
                ctx_local = SqlEvaluationContext(fields=strm.getFields(),
                                                 table_aliases=self.select_spec.getAliasToTableMapping())
                self.cacheable = self.select_spec.ok_to_cache_as_subquery(ctx_local)
            select_result = [row[0] for row in strm.getRowIterator()]
            if self.cacheable:
                ctx.cache[self.id] = select_result
        return select_result

    def eval(self, ctx):
        v = self.getValueList(ctx)
        if not v:
            return None
        if len(v) == 1:
            return v[0]
        return v

    def clone(self):
        return Node_Select(self.select_spec)

    def simplify(self, context):
        self.select_spec.simplify(context)
        return self

    def to_sql(self, flavor: str=None):
        return "({0})".format(self.select_spec.to_sql(flavor))


class Node_InSelect(Node_Select):
    def __init__(self, left, select_spec):
        Node_Select.__init__(self, select_spec)
        self.children = [left]

    def eval(self, ctx):
        select_result = self.getValueList(ctx)
        v_l = self.children[0].eval(ctx)
        return v_l in select_result

    def clone(self):
        return Node_InSelect(self.children[0].clone(), self.select_spec)

    def to_sql(self, flavor: str=None):
        return "{0} in ({1})".format(self.children[0].to_sql(flavor), self.select_spec.to_sql(flavor))


class Node_List(Node):
    def __init__(self, children=None):
        self.children = children or []

    def eval(self, ctx):
        return [v.eval(ctx) for v in self.children]

    def clone(self):
        return Node_List([c.clone() for c in self.children])

    def to_sql(self, flavor: str=None):
        return "({0})".format(", ".join([c.to_sql(flavor) for c in self.children]))


class Node_Op(Node):
    def __init__(self, operator, add_children=None):
        self.operator = operator
        self.children = add_children or []
        self.null_if_any_null = True
        f = OPERATORS.get(self.operator)
        if self.operator == "or":
            self.null_if_any_null = False
        if not f:
            def unimpl(l, r):
                raise Exception("operator not implemented yet: " + self.operator)
            f = unimpl
        self.f = f

    def eval(self, ctx):
        left = self.children[0].eval(ctx)
        right = self.children[1].eval(ctx)
        if self.null_if_any_null and (left is None or right is None):
            return None
        return self.f(left, right)

    def clone(self):
        return Node_Op(self.operator, self._cloneOfChildren())

    def to_sql(self, flavor: str=None):
        prec = OP_PRECEDENCE.get(self.operator, -1)
        def child(n):
            parens = False
            ch = self.children[n]
            if isinstance(ch, Node_Op):
                c_prec = OP_PRECEDENCE.get(ch.operator, -1)
                if c_prec < prec:
                    # if child operator has lower precedence it needs parentheses
                    parens = True
            if parens:
                return f"({ch.to_sql(flavor)})"
            else:
                return ch.to_sql(flavor)
        return child(0) + ' ' + self.operator + ' ' + child(1)


class Node_Op_Is(Node):
    OP_IS = "is"
    OP_IS_NOT = "is not"
    def __init__(self, operator, add_children=None):
        self.operator = operator
        self.children = add_children or []
        if self.operator == self.OP_IS:
            self.f = lambda left, right: left == right
        elif self.operator == self.OP_IS_NOT:
            self.f = lambda left, right: left != right

    def eval(self, ctx):
        left = self.children[0].eval(ctx)
        right = self.children[1].eval(ctx)
        return self.f(left, right)

    def clone(self):
        return Node_Op_Is(self.operator, self._cloneOfChildren())

    def to_sql(self, flavor: str=None):
        return self.children[0].to_sql(flavor) + ' ' + self.operator + ' ' + self.children[1].to_sql(flavor)


class Node_Case(Node):
    def __init__(self, when_then_else):
        self.children = when_then_else or []

    def eval(self, ctx):
        for idx in range(0, len(self.children) - 1, 2):
            if self.children[idx].eval(ctx):
                return self.children[idx + 1].eval(ctx)
        if len(self.children) % 2 == 1:
            return self.children[-1].eval(ctx)

    def clone(self):
        return Node_Case(self._cloneOfChildren())

    def to_sql(self, flavor: str=None):
        parts = ["CASE"]
        for idx in range(0, len(self.children) - 1, 2):
            parts.append("WHEN {0} THEN {1}".format(self.children[idx].to_sql(flavor), self.children[idx + 1].to_sql(flavor)))
        if len(self.children) % 2 == 1:
            parts.append("ELSE {0}".format(self.children[-1].to_sql(flavor)))
        parts.append("END")
        return " ".join(parts)


class SqlOrderBy(object):
    def __init__(self):
        self.levels = []

    def addLevel(self, expr, ascending=True):
        self.levels.append((expr, ascending))

    def compare(self, rec_l, rec_r, ctx):
        for level in self.levels:
            v_l = level[0].eval(ctx.derive(record=rec_l))
            v_r = level[0].eval(ctx.derive(record=rec_r))
            c = _cmp(v_l, v_r)
            if not level[1]:
                c = -c
            if c != 0:
                return c
        return 0

    def to_sql(self, flavor: str=None):
        out = []
        for level in self.levels:
            part = level[0].to_sql(flavor)
            if not level[1]:
                part += " DESC"
            out.append(part)
        return ", ".join(out)


def _parse_time(timestr, ignoretz=True):
    if timestr == "now":
        return time.time()
    dt = parse_date(timestr, ignoretz=ignoretz)
    return dt.timetuple()


def _like(value, ptn):
    ptn = str(ptn)
    ptn = re.sub(r'([.+\-*?\[\]()|{\}~^$])', r'\\\1', ptn)
    ptn = ptn.replace("%", ".*").replace("_", ".")
    return re.match(ptn, str(value)) is not None


def _ilike(value, ptn):
    ptn = str(ptn)
    ptn = re.sub(r'([.+\-*?\[\]()|{\}~^$])', r'\\\1', ptn)
    ptn = ptn.replace("%", ".*").replace("_", ".")
    return re.match(ptn, str(value), re.IGNORECASE) is not None


class SqlAggregator(object):
    """
    Base class for aggregation methods.
    """
    def reset(self):
        """
        Reset state for another aggregation run.
        """

    def applyValue(self, value):
        """
        Aggregate one more value.
        """

    def getResult(self):
        """
        Get final aggregated result.
        """


class _AggMin(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None

    def applyValue(self, value):
        if value is not None and (self.value is None or value < self.value):
            self.value = value

    def getResult(self):
        return self.value


class _AggMax(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None

    def applyValue(self, value):
        if value is not None and (self.value is None or value > self.value):
            self.value = value

    def getResult(self):
        return self.value


class _AggCount(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = 0

    def applyValue(self, value):
        if value is not None:
            self.value += 1

    def getResult(self):
        return self.value


class _AggCountDistinct(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.values = set()

    def applyValue(self, value):
        if value is not None:
            if isinstance(value, list):
                value = tuple(value)
            self.values.add(value)

    def getResult(self):
        return len(self.values)


class _AggSum(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = 0

    def applyValue(self, value):
        if isinstance(value, (int, float)):
            self.value += value

    def getResult(self):
        return self.value


class _AggAvg(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = 0
        self.count = 0

    def applyValue(self, value):
        if isinstance(value, (int, float)):
            self.value += value
            self.count += 1

    def getResult(self):
        if self.count:
            return float(self.value) / self.count


class _AggMedian(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.values = []

    def applyValue(self, value):
        if value is not None:
            self.values.append(value)

    def getResult(self):
        self.values.sort()
        n = len(self.values)
        if not n:
            return None
        if n == 1:
            return self.values[0]
        if n % 2 == 1:
            return self.values[n//2]
        v0 = self.values[n//2-1]
        v1 = self.values[n//2]
        if isinstance(v0, str):
            return v0 + " "
        return (v0+v1)/2


class _AggStdev(SqlAggregator):
    def __init__(self):
        self.reset()

    def reset(self):
        self.mean = 0.0
        self.squares = 0.0
        self.n = 1

    def applyValue(self, value):
        if isinstance(value, (int, float)):
            t_m = self.mean
            self.mean += (value - t_m) / self.n
            self.squares += (value - t_m) * (value - self.mean)
            self.n += 1

    def getResult(self):
        if self.n < 3:
            return None
        return math.sqrt(self.squares / (self.n - 2))


AGGREGATORS = {
    "min": _AggMin,
    "max": _AggMax,
    "count": _AggCount,
    "count_distinct": _AggCountDistinct,
    "sum": _AggSum,
    "total": _AggSum,
    "avg": _AggAvg,
    "average": _AggAvg,
    "median": _AggMedian,
    "stdev": _AggStdev
}
AGGREGATE_FNS = frozenset(AGGREGATORS.keys())


def _is_literal(node):
    if isinstance(node, Node_Literal):
        return True
    if hasattr(node, "children"):
        for sub in node.children:
            if not _is_literal(sub):
                return False
        return True
    return False


def simplify_expression(node, context):
    """
    Simplify an expression.  Currently only collapses operations between literals.
    """
    def simplify(node):
        if not isinstance(node, Node_Literal) and _is_literal(node):
            value = node.eval(context)
            return Node_Literal(value)
        if hasattr(node, "children"):
            node.children = [simplify(sub) for sub in node.children]
        return node
    return simplify(node)


def has_any_aggregators(node):
    """
    Detect the presence of aggregating functions.
    """
    if isinstance(node, Node_Function) and node.aggregator:
        return True
    if hasattr(node, "children"):
        for sub in node.children:
            if has_any_aggregators(sub):
                return True
    return False


def uses_aggregation(select_spec):
    """
    Check whether a SELECT uses any aggregation.
    """
    # if grouping is requested, then we don't need to look further
    if select_spec.group_by:
        return True
    # check for aggregation functions
    if not select_spec.fields:
        return False
    for f in select_spec.fields:
        if has_any_aggregators(f[0]):
            return True
    return False


def _cmp(a, b):
    if a is None and b is None:
        return 0
    if b is None:
        return -1
    if a is None:
        return 1
    try:
        return (a > b) - (a < b)
    except TypeError:
        a, b = str(a), str(b)
        return (a > b) - (a < b)


def soundex(name, len=4):
    """ soundex module conforming to Knuth's algorithm
        implementation 2000-12-24 by Gregory Jorgensen
        public domain

        source: http://code.activestate.com/recipes/52213-soundex-algorithm/
    """
    #
    name = strip_accents(name)
    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    sndx = ''
    fc = ''
    # translate alpha chars in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc: fc = c  # remember first letter
            d = digits[ord(c) - ord('A')]
            # duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d
    # replace first digit with first alpha character
    sndx = fc + sndx[1:]
    # remove all 0s from the soundex code
    sndx = sndx.replace('0', '')
    # return soundex code padded to len characters
    return (sndx + (len * '0'))[:len]


### copied from MiscUtils, to make sql package standalone ###
PTN_ANYUNICODE = re.compile(r'[\x80-\xFF]')
PTN_ANYUNICODE_u = re.compile(r'[\u0080-\uFFFF]')


def strip_accents(input_str):
    if isinstance(input_str, str):
        if PTN_ANYUNICODE.search(input_str) is None:
            return input_str
    else:
        if PTN_ANYUNICODE_u.search(input_str) is None:
            return str(input_str)
    # source: http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    s = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return str(s.encode('ASCII', 'ignore'))


