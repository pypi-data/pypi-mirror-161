from .parser import SqlParser


def parse_insert(sql: str):
    """
    Parsing of 'INSERT INTO'.  Returns:
      table_name
      field_list
      a generator for the list of rows
    """
    parser = SqlParser(sql)
    if not parser.skip_keyword("INSERT"):
        parser.report_error("expected 'insert'")
    if not parser.skip_keyword("INTO"):
        parser.report_error("expected 'into' after 'insert'")
    table_name = parser.parse_table_name()
    parser.skip_punct("(", error_if_missing=True)
    fields = []
    while True:
        fields.append(parser.any_keyword("field name"))
        if not parser.skip_punct(','):
            break
    if not parser.skip_punct(')'):
        parser.report_error("expected ')' after field list")
    if not parser.skip_keyword("VALUES"):
        parser.report_error("expected values for insert")
    def rows():
        while True:
            parser.skip_punct("(", error_if_missing=True)
            values = []
            while True:
                values.append(parser.parse_expr().eval(None))
                if not parser.skip_punct(','):
                    break
            if not parser.skip_punct(')'):
                parser.report_error("expected ')' after value list")
            yield values
            if not parser.skip_punct(','):
                break
        if parser.cur_token():
            parser.report_error("expected end of statement")
    return table_name, fields, rows()


def parse_create_db(sql: str):
    """
    Check for a CREATE DATABASE statement.  Returns None, or a tuple with information about the statement.
    """
    parser = SqlParser(sql)
    if not parser.skip_keyword("CREATE"):
        return
    if not parser.skip_keyword("DATABASE"):
        return
    if_not_exists = False
    if parser.skip_keyword("IF"):
        if not parser.skip_keyword("NOT"):
            parser.report_error("expected 'not'")
        if not parser.skip_keyword("EXISTS"):
            parser.report_error("expected 'exists'")
        if_not_exists = True
    db_name = parser.any_keyword("database name")
    if parser.cur_token():
        parser.report_error("expected end of statement")
    return db_name, if_not_exists


def parse_delete(sql: str):
    """
    Parsing of 'DELETE'.  Returns:
      table_name
      where clause
    """
    parser = SqlParser(sql)
    if not parser.skip_keyword("DELETE"):
        parser.report_error("expected 'delete'")
    if not parser.skip_keyword("FROM"):
        parser.report_error("expected 'from' after 'delete'")
    table_name = parser.parse_table_name()
    where = None
    if parser.skip_keyword("WHERE"):
        where = parser.expect_expr()
    if parser.cur_token():
        parser.report_error("expected end of statement")
    # TODO limit could also be supported here
    return table_name, where


def parse_drop_table(sql: str):
    """
    Parsing of 'DROP TABLE'.  Returns:
      table_name
      if_exists flag
    """
    parser = SqlParser(sql)
    if not parser.skip_keyword("DROP"):
        parser.report_error("expected 'drop'")
    if not parser.skip_keyword("TABLE"):
        parser.report_error("expected 'table'")
    if_exists = parser.skip_keyword(["IF", "EXISTS"])
    table_name = parser.parse_table_name()
    if parser.cur_token():
        parser.report_error("expected end of statement")
    return table_name, if_exists
