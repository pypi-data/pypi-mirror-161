import os.path

from dslibrary.sql.file_sql_wr import file_sql_write
from dslibrary.transport.to_local import DSLibraryLocal
from dslibrary.utils.dbconn import Connection
from dslibrary.utils.file_utils import is_breakout_path


def connect_to_folder_as_database(folder: str, for_write: bool=False, sql_flavor: str="mysql", **kwargs):
    """
    Each file in the folder is a table.

    :param folder:      Folder containing files.
    :param for_write:   Enable writes.
    :param sql_flavor:  Which dialect to emulate.
    :param kwargs:
    :return:        A DBI-style connection instance.
    """
    dsl = DSLibraryLocal(filesystem_root=folder)
    def file_exists(fn: str):
        return os.path.exists(os.path.join(folder, fn))
    def table_reader(table_spec: tuple):
        table_name = table_spec[-1]
        if is_breakout_path(table_name):
            return
        # allow tables to match CSV files
        # TODO what about other file formats?
        if not table_name.endswith(".csv") and file_exists(table_name+".csv"):
            table_name += ".csv"
        return dsl.load_dataframe(os.path.join(folder, table_name))
    def table_writer(table_spec: tuple, mode: str=None):
        if is_breakout_path(table_spec[-1]):
            return
        return dsl.open_resource(os.path.join(folder, table_spec[-1]), mode=mode)
    def read(sql, parameters):
        df = dsl.sql_select(sql, parameters, table_loader=table_reader)
        rows = df.itertuples(index=False, name=None)
        # TODO iteration in chunks would make more efficient use of memory - see read_more below
        return list(df.columns), list(rows), None
    def write(sql, parameters):
        file_sql_write(table_writer, sql, parameters)
    return Connection(read=read, write=write if for_write else None, read_more=None, flavor=sql_flavor)
