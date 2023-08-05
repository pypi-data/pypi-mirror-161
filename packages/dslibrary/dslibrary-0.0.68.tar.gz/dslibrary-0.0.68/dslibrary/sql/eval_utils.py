"""
Utilities for evaluation of SQL.
"""
from dslibrary.sql.data import SqlDataSupplier
from dslibrary.sql.exceptions import SqlException_DataSourceNotFound

# operators
from dslibrary.sql.misc import cmp_table_names

OPS = [
    ["or"],
    ["and"],
    ["=", "==", "!=", "<>", "is", "is not", "in", "not in", "like", "not like", "ilike", "not ilike", "glob", "not glob", "match",
     "not match", "regexp", "not regexp"],
    ["<", "<=", ">", ">="],
    ["<<", ">>", "&", "|"],
    ["+", "-"],
    ["*", "/", "%"],
    ["||"]
]
OPS_ALL = set([op for ops in OPS for op in ops]) | {"between"}
OP_PRECEDENCE = {op: n for n, opGroup in enumerate(OPS) for op in opGroup}
UOPS = {"-", "+", "~", "not"}


class SqlEvaluationContext(object):
    class NullCache(object):
        def __getitem__(self, item):
            """ All requests return None """

        def __setitem__(self, key, value):
            """ Storing item has no effect """

        def get(self, item):
            """ Cache is always empty """

        def __contains__(self, item):
            return False

    def __init__(self, parent=None, record=None, fields=None, table_aliases=None, compiler=None, data_suppliers=None,
                 aggregate=None, debug_level=None, ext_vars=None, cache=None):
        self.parent = parent
        self._record = record
        self._fields = fields
        self._table_aliases = table_aliases
        self._compiler = compiler
        self._data_suppliers = data_suppliers
        self._cache = cache
        self._debug_level = debug_level
        self._aggregate = aggregate
        self._ext_vars = ext_vars

    def getRoot(self):
        """
        Finds the topmost context in a tree.
        """
        if self.parent:
            return self.parent.getRoot()
        return self

    def _get_debug_level(self):
        return self.getRoot()._debug_level or 0

    def _set_debug_level(self, v):
        self.getRoot()._debug_level = v

    debugLevel = property(_get_debug_level, _set_debug_level)
    """
    Determines whether to display diagnostic information.  This value
    is managed only at the root level.
    """

    @property
    def cache(self):
        """
        Information about the current operation can be cached here.  This accessor returns the
        cache from the topmost context object, i.e. a global cache for the whole operation.
        """
        obj = self.getRoot()
        if obj._cache is None:
            obj._cache = {}
        return obj._cache

    @property
    def fieldCache(self):
        """
        Returns the cache for the topmost context which defines a list of fields.
        """
        if self._fields is not None:
            if self._cache is None:
                self._cache = {}
            return self._cache
        if self.parent:
            return self.parent.fieldCache

    def _get_record(self):
        if self._record:
            return self._record
        if self.parent:
            return self.parent.record

    def _set_record(self, v):
        self._record = v

    record = property(_get_record, _set_record)
    """
    The current data row.
    """

    def _get_aggregate(self):
        if self._aggregate is not None:
            return self._aggregate
        if self.parent:
            return self.parent.aggregate
        return True

    def _set_aggregate(self, v):
        self._aggregate = v

    aggregate = property(_get_aggregate, _set_aggregate)
    """
    Whether to apply values to aggregators, or to only return current values.
    """

    def _get_compiler(self):
        if self._compiler:
            return self._compiler
        if self.parent:
            return self.parent.compiler

    def _set_compiler(self, v):
        self._compiler = v

    compiler = property(_get_compiler, _set_compiler)
    """
    A compiler which can be used to create data manipulation structures on the fly.
    """

    def _get_data_suppliers(self):
        if self._data_suppliers is not None:
            return self._data_suppliers
        if self.parent:
            return self.parent.data_suppliers
        else:
            self._data_suppliers = []
            return self._data_suppliers

    def _set_data_suppliers(self, v):
        self._data_suppliers = v

    data_suppliers = property(_get_data_suppliers, _set_data_suppliers)
    """
    The list of data suppliers which stream data from available sources.
    """

    def _get_fields(self):
        if self._fields:
            return self._fields
        if self.parent:
            return self.parent.fields

    def _set_fields(self, v):
        self._fields = v

    fields = property(_get_fields, _set_fields)
    """
    Definitions for each field in the current row or stream.
    """

    def _get_table_aliases(self):
        if self._table_aliases is not None:
            return self._table_aliases
        if self.parent:
            return self.parent.table_aliases
        self._table_aliases = {}
        return self._table_aliases

    def _set_table_aliases(self, v):
        self._table_aliases = v

    table_aliases = property(_get_table_aliases, _set_table_aliases)
    """
    A set of aliases that apply to all known tables.  This is a mapping from aliases to full table names.
    """

    def getNamedValue(self, fieldSpec):
        """
        Look for the given value, which is in the form of a tuple of tableName/tableAlias and fieldName/fieldAlias.

        If the value is not found in the current record, we check the parent context, which may contain a different
        record, in the case where we are a subquery context.

        :param fieldSpec:  A tuple indicating a table and field name.
        """
        idx = find_field_in_list(fieldSpec, self)
        if idx >= 0:
            if self.record and idx < len(self.record):
                return self.record[idx]
        elif self.parent:
            return self.parent.getNamedValue(fieldSpec)

    def namedValueAvailable(self, fieldSpec):
        """
        Look for the given value, which is in the form of a tuple of tableName/tableAlias and fieldName/fieldAlias.

        If the value is not found in the current record, we check the parent context, which may contain a different
        record, in the case where we are a subquery context.
        """
        idx = find_field_in_list(fieldSpec, self)
        if idx >= 0:
            return True
        elif self.parent:
            return self.parent.namedValueAvailable(fieldSpec)
        return False

    def getExtVar(self, name: str):
        """
        Get the value of a named external variable.
        """
        if not self._ext_vars or name not in self._ext_vars:
            raise Exception("variable not found: %s" % name)
        return self._ext_vars.get(name)

    def derive(self, record=None, fields=None, tableAliases=None, aggregate=None, cache=None):
        """
        Create a new derived context which inherits all properties from 'self'.
        """
        return SqlEvaluationContext(parent=self, record=record, fields=fields, table_aliases=tableAliases,
                                    aggregate=aggregate, ext_vars=self._ext_vars, cache=cache)

    def addDataSupplier(self, supplier):
        """
        All data ultimately comes from the suppliers added here.
        """
        assert isinstance(supplier, SqlDataSupplier)
        self.data_suppliers.append(supplier)

    def findDataSource(self, tableSpec, errorIfNotFound=True):
        """
        Find a data source from one of the registered data suppliers.
        """
        for supplier in self.data_suppliers:
            found = supplier.getTableStream(tableSpec)
            if found:
                return found
        if errorIfNotFound:
            raise SqlException_DataSourceNotFound(
                "data source not found: {0}".format(".".join(filter(lambda x: x, tableSpec)) if tableSpec else "None"))


def find_field_in_list(field_spec, context):
    """
    Find the index of a matching field.
    :param field_spec:   A tuple with at least a field name and optionally a database and table name.
    :param context:     A context which contains a field list to scan.
    :return:  -1 if not found, or index in field list.
    """
    if isinstance(field_spec, str):
        field_spec = (field_spec,)
    if not context or not context.fields:
        return -1

    field_cache = context.fieldCache
    if field_cache is not None:
        out = field_cache.get(field_spec)
        if out is not None:
            return out
        out = _find_field_in_list(field_spec, context)
        field_cache[field_spec] = out
        return out
    else:
        return _find_field_in_list(field_spec, context)


def _find_field_in_list(field_spec, context):
    table_spec = field_spec[:-1] if len(field_spec) > 1 else None
    field_name = field_spec[-1]
    # look up table name from alias
    derived_alias = None
    if table_spec and context.table_aliases:
        derived_alias = context.table_aliases.get(table_spec[-1])
        if isinstance(derived_alias, (tuple, list)):
            derived_alias = derived_alias[-1]
    # scan
    n_best, v_best = -1, 0
    # match field alias first
    for n, field in enumerate(context.fields):
        w = match_spec_to_field(table_spec, field_name, field, derived_alias)
        if w > v_best:
            n_best, v_best = n, w
    return n_best


def match_spec_to_field(table_spec, field_spec, field, derived_alias=None):
    """
    Compare a requested field with an available field.
    :param table_spec:  A tuple giving the components of a table, i.e. (database,table) or (table,).  The table name
            may also be the alias for a table.
    :param field_spec:  A string with the name of a field or an alias.
    :param field:      The available field to which we are comparing.
    :param derived_alias:  The implied alias of the supplied table name.  This alias may be from a different context so
            it is to be weighed lightly.
    :return:  A weighting, with higher numbers indicating better matches, and 0 indicating no match.
    """
    # compare field name - at least a loose match is mandatory
    w_f = _field_match_ranking(field_spec, field)
    if not w_f:
        return 0
    # check database name
    w_d = _database_match_ranking(table_spec, field)
    if w_d < 0:
        return 0
    # compare table name
    if not table_spec or not table_spec[-1]:
        # no table spec at all - this is the weakest match
        w_t = 0
    else:
        w_t = _table_match_ranking(table_spec, field, derived_alias)
        if w_t == 0:
            return 0
        if w_t == 3 and w_d == 0:
            # if there's a table alias we don't need the database to be specified
            w_d = 1
    # add the points together
    return w_f + w_t + w_d


def _field_match_ranking(field_spec, field):
    # compare field name
    if field.alias and cmp_table_names(field_spec, field.alias):
        # match on alias is best
        return 3
    elif cmp_table_names(field_spec, field.field):
        if not field.alias:
            # match on field name is 2nd best
            return 2
        else:
            # if there's an alias but we match the field name that's 'acceptable' but the weakest possible match
            return 1
    else:
        return 0


def _table_match_ranking(table_spec, field, derived_alias):
    if field.table_alias and cmp_table_names(table_spec[-1], field.table_alias):
        # match on table alias is the best
        return 3
    elif cmp_table_names(table_spec[-1], field.table):
        if not field.table_alias:
            # 2nd best is match on table name when there is no table alias
            return 2
        else:
            # 3rd is match on table name when we could have matched an alias
            return 1
    else:
        if cmp_table_names(derived_alias, field.table_alias):
            # 4th - indirectly implied table alias matches
            return 1
        else:
            # mismatch on table name: reject
            return 0


def _database_match_ranking(table_spec, field):
    db_name = table_spec[-2] if table_spec and len(table_spec) > 1 else None
    if field.database or db_name:
        if field.database and db_name:
            # if a database name is specified on both sides it must match
            if not cmp_table_names(db_name, field.database):
                return -1
            else:
                # proper match on database
                return 2
        else:
            # a database name is specified on only one side - this is not great but we can work around it
            return 0
    else:
        # no database specified
        return 1
