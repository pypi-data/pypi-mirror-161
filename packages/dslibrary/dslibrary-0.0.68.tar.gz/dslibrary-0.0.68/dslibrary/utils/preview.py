"""
Get a quick overview of a file with basic information like column and row counts.
"""
import dslibrary
import copy


class DataPreview(object):
    """
    See data_preview().
    """
    def __init__(self, n_rows, n_cols, col_names, col_types, sample_rows, n_rows_estimated):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.col_names = col_names
        self.col_types = col_types
        self.sample_rows = sample_rows
        self.n_rows_estimated = n_rows_estimated

    def to_json(self):
        return self.__dict__


def data_preview(access: dict, preview_size=20000, capture_rows=10, max_cols=100):
    """
    Gather basic preview information about a data source.

    :param access:      Arguments for dslibrary.load_dataframe()
    :param preview_size: Maximum number of bytes to read from files.
    :param capture_rows: Number of rows to sample.
    :param max_cols:     Maximum number of columns to consider.
    :returns:  A DataPreview instance.
    """
    access = copy.deepcopy(access)
    truncated = False
    if "sql_table" in access:
        raise NotImplementedError("not supported yet: sql_table")
    if "sql_source" in access:
        flavor = access.get("sql_flavor")
        # count rows
        access['resource_name'] = f"select count(*) as row_count from ({access['resource_name']})"
        df = dslibrary.load_dataframe(**access)
        n_rows = df.row_count[0]
        # get sample rows
        if flavor == "mssql":
            access['resource_name'] = f"select top {capture_rows} * from ({access['resource_name']})"
        else:
            access['resource_name'] = f"select * from ({access['resource_name']}) limit {capture_rows}"
        df = dslibrary.load_dataframe(**access)
    else:
        if "format_options" not in access:
            access["format_options"] = {}
            access["format_options"]["chunksize_bytes"] = preview_size
        try:
            df_stream = dslibrary.load_dataframe(**access)
            df = next(df_stream)
            try:
                next(df_stream)
                truncated = True
            except StopIteration:
                truncated = False
        except Exception as err:
            if err.__class__.__name__ == "DSLibraryDataFormatException" and "chunksize" in str(err):
                # cannot read in chunks (i.e. a JSON file)
                access["format_options"].pop("chunksize", None)
                access["format_options"].pop("chunksize_bytes", None)
                df = dslibrary.load_dataframe(**access)
            else:
                raise
        n_rows = len(df)
        if truncated:
            tot_size = _size(access)
            if tot_size:
                n_rows = int(n_rows * tot_size / min(tot_size, preview_size))
            else:
                n_rows = -1
    captured = list(map(lambda row: row[:max_cols], df.head(capture_rows).itertuples(name=None, index=False)))
    col_names = list(df.columns)
    col_dtypes = list(map(str, df.dtypes))
    return DataPreview(n_rows, len(col_names), col_names[:max_cols], col_types=col_dtypes[:max_cols], sample_rows=captured, n_rows_estimated=truncated)


def _size(access: dict):
    with dslibrary.open_resource(**access, mode='rb') as f:
        if f.seekable():
            f.seek(0, 2)
            return f.tell()
