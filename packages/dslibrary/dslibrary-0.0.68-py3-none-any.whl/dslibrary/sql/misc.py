"""
General purpose utilities with no serious dependencies.
"""
import re
import time
import datetime
import dateutil.parser
import urllib.parse

from dslibrary.utils.format_sniffer import find_url_extension

SQL_PARTS = re.compile(r'(/\*.*?\*/|"([^"]|"")*?"|`[^`]*?`|\'([^\']|\'\')*?\'|((?!/\*)(?!%s)(?!\?)[^;\'"`])+|;|%s|\?)',
                       re.DOTALL)
PTN_NOQUOTES = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
PTN_NOQUOTES_PG = re.compile(r'^[a-z_][a-z0-9_]*$')


def sql_split(operation, parameters=None):
    """
    Break apart SQL statements.  Returns a generator of SQL strings.
    """
    params_in = list(parameters or [])
    bits = []
    params = []
    for part in SQL_PARTS.finditer(operation):
        bit = part.group(0)
        if bit == ";":
            if bits:
                yield "".join(bits).strip(), params
            bits.clear()
            params = []
        else:
            if bit in {"?", "%s"}:
                params.append(params_in.pop(0) if params_in else None)
            bits.append(bit)
    if bits:
        yield "".join(bits).strip(), params


def sql_verb(sql: str):
    """
    Determine what the 'verb' is for a SQL statement (SELECT, INSERT, etc..)
    """
    for part in SQL_PARTS.finditer(sql):
        bit = part.group(0).strip()
        if bit.startswith("/*"):
            continue
        return re.split(r'\s+', bit)[0].upper()
    return ""


def is_sql_read_operation(operation):
    """
    Detect a read-only SQL operation.
    """
    valid = False
    for stmt, _ in sql_split(operation):
        verb = sql_verb(stmt)
        if verb not in ("SELECT", "SHOW", "DESCRIBE"):
            return False
        valid = True
    return valid


def sql_enquote_id(s: (str, list, tuple), mode: str=None, always: bool=False, dotted: bool=False):
    """
    Enquote an identifier (table or column name) according to different conventions.
    :param s:       What to enquote.
    :param mode:    'mysql', 'postgres', 'ansi', ...
    :param always:  True to use quotes even when not required.
    :param dotted:  True when the name may contain multiple components, i.e. database.schema.table.  Otherwise dots are
                    considered part of the name to enquote.
    :return:    Identifier, quoted if necessary.
    """
    if isinstance(s, (list, tuple)):
        return ".".join(map(lambda sn: sql_enquote_id(sn, mode=mode, always=always), s))
    if dotted:
        return ".".join(map(lambda s1: sql_enquote_id(s1, mode=mode, always=always), s.split(".")))
    if s == "*" or s.startswith("*["):
        # special cases
        return s
    if (PTN_NOQUOTES_PG if mode == "postgres" else PTN_NOQUOTES).match(s) is not None and not always:
        return s
    # NOTE: For 'mssql', the old style is to use '[]' around identifiers, which we follow.
    #  - there is a flag to have it support double quotes (the ISO standard) but one can't count on it being set
    if mode == "mssql":
        return "[" + s.replace("[", "[[").replace("]", "]]") + "]"
    # we enquote file-based data sources like MySQL for an obscure reason:
    # - pandas.read_sql() strips double-quotes out of SQL!
    q = '`' if mode in {"mysql", "s3", "abfs", "abs", "azureblob", "bigquery"} else '"'
    return "%s%s%s" % (q, s.replace(q, q+q), q)


def is_valid_field_name(field_name: str, mode: str=None):
    """
    Check whether a field name is allowed for a given target dialect.
    :param field_name:  Name of proposed field name.
    :param mode:        Dialect name -- see sql_enquote_id().
    """
    if not field_name:
        return False
    rgx = None
    if mode == "bigquery":
        # see https://cloud.google.com/bigquery/docs/schemas
        rgx = r'^[a-zA-Z_][a-zA-Z_0-9]{,127}$'
    if mode == "mysql":
        rgx = r'^[^\`\0\255\./\\]{,64}$'
    if mode == "postgres":
        rgx = r'^.{,63}$'
    if rgx and not re.match(rgx, field_name):
        return False
    return True


def is_valid_table_name(table_name: str, mode: str=None):
    """
    Check whether a table name is allowed for a given target dialect.
    """
    if not table_name:
        return False
    rgx = None
    if mode == "bigquery":
        # see https://cloud.google.com/bigquery/docs/tables
        rgx = r'^[a-zA-Z_0-9]{,1024}$'
    if mode == "mysql":
        rgx = r'^[^\`\0\255\./\\]{,64}$'
    if mode == "postgres":
        # ALSO: reserved words: Appendix B of the PostgreSQL User's Guide.
        rgx = r'^.{,63}$'
    if rgx and not re.match(rgx, table_name):
        return False
    return True


def enquote_string_literal(v):
    """
    Enquote a string for SQL.
    """
    v0 = str(v).replace("'", "''")
    p = 0
    parts = ["'"]
    for c in re.finditer(r'([\x00-\x1F\x7F-\u7fff])', v0):
        parts.append(v0[p:c.start()])
        parts.append("'||char(%d)||'" % ord(c.group(1)))
        p = c.end()
    parts.append(v0[p:])
    parts.append("'")
    out = "".join(parts)
    if out.endswith("||''"):
        out = out[:-4]
    return out


def _to_time_number(dt):
    if isinstance(dt, (int, float)):
        return dt
    elif isinstance(dt, tuple):
        return time.mktime(dt)
    elif isinstance(dt, (datetime.datetime, datetime.date)):
        return dt.timestamp()
    else:
        return


def parse_iso_datetime(v: (str, float, datetime.datetime), ignore_error: bool=False):
    """
    Parse date/time formats and produce a date number in time.time() format (seconds past 1970).
    """
    if not isinstance(v, str):
        return _to_time_number(v)
    try:
        dt = dateutil.parser.parse(v.upper(), ignoretz=True)
        return (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    except Exception:
        if ignore_error:
            return
        raise


def cmp_table_names(a, b):
    """
    How to compare table and field names.  Ignores case.
    """
    if a is None or b is None:
        return False
    return a.lower() == b.lower()


def loose_table_match(value, listOrSetOrDict):
    """
    Find the closest match.
    """
    if value is None or listOrSetOrDict is None:
        return None
    # check for exact match
    if value in listOrSetOrDict:
        return value
    # scan for inexact match
    for k in listOrSetOrDict:
        if cmp_table_names(value, k):
            return k


def table_name_from_table_spec(table_spec: (str, tuple)):
    """
    Extract the name of a table from a full table specification.
    """
    if not table_spec:
        return
    return table_spec if isinstance(table_spec, str) else table_spec[-1]


def format_options_for_table(format_options: dict, table_spec: (tuple, str)):
    """
    Given a set of query-wide options, and a table specification, determine which options
    apply to the given table.  Note that the table name itself can contain options, so these
    are also extracted and applied.
    :param format_options:      A {} mapping table names to option {}s, and with the key "" representing
                                default options.
    :param table_spec:          Table specification, a tuple with parts like database, schema and table name.
    :return:        A {} with options appropriate to the indicated table.
    """
    if not table_spec:
        return
    table_name = table_spec if isinstance(table_spec, str) else table_spec[-1]
    # options can be transmitted via table name, using URI conventions
    if '#' in table_name:
        table_name, qs = table_name.split('#', maxsplit=1)
        uri_args = {k: vv[-1] if len(vv) == 1 else vv for k, vv in urllib.parse.parse_qs(qs).items()}
    else:
        uri_args = {}
    if format_options:
        if table_name in format_options:
            opts = format_options[table_name]
        else:
            opts = format_options.get("", {})
    else:
        opts = {}
    opts.update(uri_args)
    # guess file format from table name
    if "format" not in opts and "." in table_name:
        opts["format"] = find_url_extension(table_name)
    return opts


def str_to_var_name(s: str) -> str:
    """
    Convert an arbitrary string into a valid python variable name.
    """
    def xlt(m):
        n = ord(m.group(0))
        return f"_{hex(n//16)[2:]}{hex(n%16)[2:]}"
    out = re.sub(r'[^a-zA-Z0-9]', xlt, s)
    if not out or out[0].isdigit():
        out = "__" + out
    return out


def var_name_to_str(s: str) -> str:
    """
    Convert an encoded python variable name back into a string.
    """
    def xlt(seq):
        return chr(int(seq.group(0)[1:], 16))
    if s.startswith("__"):
        s = s[2:]
    return re.sub(r'_[0-9a-f][0-9a-f]', xlt, s)
