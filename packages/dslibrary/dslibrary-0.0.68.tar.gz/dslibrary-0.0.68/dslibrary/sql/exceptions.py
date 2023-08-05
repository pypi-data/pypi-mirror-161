class SqlException(Exception):
    def __init__(self, message=None, **kwargs):
        Exception.__init__(self, message)
        self.message = message
        self.details = kwargs


class SqlException_SqlProblem(SqlException):
    """
    Problems with caller-supplied SQL.
    """
    def __init__(self, message=None, **kwargs):
        SqlException.__init__(self, message, **kwargs)


class SqlException_DataSourceNotFound(SqlException):
    def __init__(self, message=None):
        SqlException.__init__(self, message)


class SqlException_NotImplemented(SqlException):
    def __init__(self, message=None):
        SqlException.__init__(self, message)
