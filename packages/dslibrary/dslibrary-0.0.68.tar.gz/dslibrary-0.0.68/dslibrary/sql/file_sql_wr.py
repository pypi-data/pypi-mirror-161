"""
Simple SQL modifications, applied to files.
"""
import io
import pandas

import dslibrary
from dslibrary.sql.exceptions import SqlException
from dslibrary.sql.modify_sql import embed_parameters
from dslibrary.sql.parser import SqlParser
from dslibrary.sql.sql_to_pandas import SqlToPandas
from dslibrary.sql.statements import parse_insert, parse_delete


def file_sql_write(open_table_stream: callable, sql: str, parameters: list=None, format_options=None):
    """
    Run SQL against files.
    :param open_table_stream:   Method to open files for read/write/etc..
    :param sql:                 SQL to execute.
    :param parameters:          Parameters to fill into SQL.
    :param format_options:      Format details.
    """
    sql = embed_parameters(sql, parameters)
    parser = SqlParser(sql)
    if parser.skip_keyword("CREATE"):
        if parser.skip_keyword("TABLE"):
            return fsql_create_table(parser, open_table_stream)
        if parser.skip_keyword("INDEX"):
            """ ignoring CREATE TABLE """
            return
    if parser.skip_keyword("INSERT"):
        return fsql_insert(sql, open_table_stream, format_options=format_options)
    if parser.skip_keyword("DELETE"):
        return fsql_delete(sql, open_table_stream, format_options=format_options)
    if parser.skip_keyword("UPDATE"):
        """ not supported yet: UPDATE """
        pass
    elif parser.skip_keyword("DROP"):
        if parser.skip_keyword("TABLE"):
            """ not supported yet: DROP TABLE """
            pass
        if parser.skip_keyword("INDEX"):
            """ ignoring DROP INDEX """
            return
        pass
    elif parser.skip_keyword("ALTER"):
        """ not supported yet: ALTER TABLE """
        pass
    parser.report_error(f"unsupported SQL: {sql}")


def fsql_create_table(parser, opener):
    """
    CREATE TABLE
    """
    if_not_exist = False
    if parser.skip_keyword("IF"):
        if not parser.skip_keyword("NOT"):
            parser.report_error("invalid create table syntax")
        if not parser.skip_keyword("EXISTS"):
            parser.report_error("invalid create table syntax")
        if_not_exist = True
    table_name = parser.any_keyword("table name")
    parser.skip_punct("(", error_if_missing=True)
    fields = []
    while True:
        field_name = parser.any_keyword("field name")
        fields.append(field_name)
        # (we ignore the data type)
        dt = parser.any_keyword("data type")
        if dt == "double" and parser.skip_keyword("precision"):
            # allow 'double precision'
            dt += " precision"
        if parser.skip_punct("("):
            parser.parse_value()
            if not parser.skip_punct(')'):
                parser.report_error("Expected ')' after data type qualifier")
        if parser.skip_keyword("NULL"):
            # we ignore nullability
            pass
        elif parser.skip_keyword("NOT") and not parser.skip_keyword("NULL"):
            parser.report_error("expected 'nullable' after 'not'")
        if not parser.skip_punct(','):
            break
    if not parser.skip_punct(')'):
        parser.report_error("expected ')' after field list")
    # flag to skip duplicate creation
    if if_not_exist:
        try:
            with opener((table_name,), 'rb') as found:
                # exists
                pass
            if found:
                return
        except Exception:
            # failure means file doesn't exist
            pass
    # creation: store a header
    with opener((table_name,), 'w') as f_w:
        content = "\t".join(fields) + "\n"
        f_w.write(content)


def fsql_insert(sql, opener, format_options=None):
    """
    INSERT INTO
    """
    table_name, fields, rows = parse_insert(sql)
    # verify table exists, read headers
    f_r = opener(table_name, 'rb')
    if not f_r:
        table = pandas.DataFrame(data=rows, columns=fields)
    else:
        with f_r:
            table = dslibrary.load_dataframe(f_r, uri=table_name[-1], format_options=format_options)
        table = pandas.concat([table, pandas.DataFrame(rows, columns=fields)])
    buf = io.StringIO()
    table.to_csv(buf, sep="\t", index=False)
    with opener(table_name, 'w') as f_w:
        f_w.write(buf.getvalue())


def fsql_delete(sql, opener, format_options=None):
    """
    DELETE rows
    """
    table_name, where = parse_delete(sql)
    # verify table exists, read headers
    f_r = opener(table_name, 'rb')
    if not f_r:
        raise SqlException(message=f"table not found: {table_name}")
    with f_r:
        table = dslibrary.load_dataframe(f_r, uri=table_name[-1], format_options=format_options)
    # delete rows
    if where:
        ctx = {"tables": {"table": table}}
        to_run = compile(SqlToPandas(f"select * from table where not({where})", local_tables="tables", pandas_only=True).code, "<code>", "exec")
        eval(to_run, ctx, ctx)
        table = ctx["_"]
    else:
        table = table[0:0]
    # regenerate table content
    buf = io.StringIO()
    table.to_csv(buf, sep="\t", index=False)
    with opener(table_name, 'w') as f_w:
        f_w.write(buf.getvalue())
