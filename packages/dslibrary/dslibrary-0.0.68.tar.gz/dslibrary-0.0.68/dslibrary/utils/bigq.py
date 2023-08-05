"""
Support for Google BigQuery.
"""
import tempfile
import json
import google.oauth2.service_account
import google.cloud.bigquery
from google.api_core.exceptions import NotFound, BadRequest, Forbidden
from google.auth.exceptions import RefreshError

import dslibrary.utils.dbconn
from dslibrary import DSLibraryException
from dslibrary.sql.misc import sql_split, sql_verb
from dslibrary.sql.modify_sql import embed_parameters
from dslibrary.sql.statements import parse_insert, parse_drop_table, parse_create_db


def create_bgq_connection(**kwargs):
    """
    Generate a DBI-compatible connection.
    :param kwargs:  See bgq_connect().
    :return:   A connection with a cursor() method, which in turn has methods like fetchmany().
    """
    read_only = bool(kwargs.get("read_only"))
    page_size = 1000
    def read(sql, params):
        _, rows = bgq_operation(kwargs, sql, params, page_size=page_size, read_only=True)
        cols = tuple((col.name, None, None, None, None, None) for col in rows.schema)
        rows, more = read_more((cols, iter(rows.pages)))
        return cols, rows, more
    def write(sql, params):
        if read_only:
            raise BadRequest(message="read-only data source")
        bgq_operation(kwargs, sql, params)
    def read_more(more):
        more_cols, more_rows = more
        rows = []
        try:
            page = next(more_rows)
            rows = list(page)
            return rows, more
        except StopIteration:
            return rows, None
    return dslibrary.utils.dbconn.Connection(read, write, read_more)


def bgq_connect(service_account: (dict, str), project: str=None, **kwargs):
    """
    Connect to BGQ, given connection properties.

    :param service_account:  Content that would normally be placed in a 'service account file'.
    :param project:  Default project.
    :returns:  A BGQ Client object.
    """
    if isinstance(service_account, str):
        service_account = json.loads(service_account)
    if not project:
        project = service_account.get("project_id")
    with tempfile.NamedTemporaryFile(mode='w') as f_tmp:
        json.dump(service_account, f_tmp)
        f_tmp.flush()
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            f_tmp.name,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        return google.cloud.bigquery.Client(
            credentials=credentials,
            project=project
        )


def bgq_operation(connection_args, sql, parameters=None, page_size=None, read_only: bool=False):
    """
    Start a read/write operation.
    :param connection_args:     See bgq_connect().
    :param sql:                 SQL to run.
    :param parameters:          Parameters for SQL.
    :param page_size:           Paging size for reads.
    :param read_only:           Prohibits write operations.
    :returns:           The client object, and the iterator for the results.
    """
    if parameters:
        # we embed the parameters ourselves - generic incoming SQL might use %s instead of ?
        # official bigquery way to embed parameters is described here:
        #   https://cloud.google.com/bigquery/docs/parameterized-queries
        sql = embed_parameters(sql, parameters)
    client = bgq_connect(**connection_args)
    job_cfg = None
    if connection_args.get("database"):
        dataset = connection_args["database"]
        if "." not in dataset and client.project:
            dataset = client.project + "." + dataset
        job_cfg = google.cloud.bigquery.QueryJobConfig(default_dataset=dataset)
    try:
        rows = []
        for stmt, _ in sql_split(sql):
            verb = sql_verb(stmt)
            if read_only and verb != "SELECT":
                raise BadRequest(message="read only data source")
            if verb == "INSERT":
                _insert(stmt, client, connection_args)
            elif verb == "SELECT":
                # note that only the results from the last select are returned
                query_job = client.query(stmt, job_config=job_cfg)
                rows = query_job.result(page_size=page_size)
            elif verb == "DROP":
                _drop_table(stmt, client, connection_args, job_cfg)
            else:
                create_db = parse_create_db(stmt)
                if create_db:
                    # database creation
                    client.create_dataset(create_db[0], exists_ok=True)
                else:
                    # all other statements, like CREATE, ALTER, ...
                    query_job = client.query(stmt, job_config=job_cfg)
                    query_job.result()
    except (NotFound, SyntaxError, BadRequest, Forbidden, RefreshError) as err:
        raise DSLibraryException(str(err))
    return client, rows


def _insert(stmt, client, connection_args):
    """
    Insert has to be done differently -- in DDL, inserts only apply to temporary tables
    """
    wr_table, wr_cols, wr_rows = parse_insert(stmt)
    fq_table = expand_bgq_table(
        wr_table, service_account=connection_args.get("service_account"),
        project=connection_args.get("project"), database=connection_args.get("database")
    )
    client.insert_rows_json(fq_table, ({col: row[idx] for idx, col in enumerate(wr_cols)} for row in wr_rows))


def _drop_table(stmt, client, connection_args, job_cfg):
    drop_tbl, drop_ifnx = parse_drop_table(stmt)
    fq_table = expand_bgq_table(
        drop_tbl, service_account=connection_args.get("service_account"),
        project=connection_args.get("project"), database=connection_args.get("database")
    )
    stmt = f"DROP TABLE {'IF EXISTS ' if drop_ifnx else ''}{fq_table}"
    query_job = client.query(stmt, job_config=job_cfg)
    query_job.result()


def expand_bgq_table(table_name: (str, tuple, list), service_account=None, project=None, database=None) -> str:
    """
    Cause a table name to be fully qualified.
    """
    if isinstance(table_name, str):
        table_name = table_name.split(".")
    if len(table_name) >= 3:
        # table_name is already fully qualified
        return '.'.join(table_name)
    if service_account and isinstance(service_account, str):
        service_account = json.loads(service_account)
    service_account = service_account or {}
    project_name = project or service_account.get("project_id")
    if not project_name:
        raise DSLibraryException("project not specified")
    if len(table_name) == 2:
        # we just need to add project
        return ".".join((project_name, table_name[0], table_name[1]))
    if len(table_name) == 1:
        # add project and database
        if not database:
            raise DSLibraryException("database not specified")
        return ".".join((project_name, database, table_name[-1]))
