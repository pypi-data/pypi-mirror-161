"""
Random access reads against dataframes using only reset and forward iterators.
"""
import numpy
import math


class DFIterator(object):
    def __init__(self, df):
        self.df = df
        self.columns = list(df.columns)
        self.re_iter = lambda: df.itertuples(index=False, name=None)
        self.iter = None
        self.pos = 0
        self.eof = False
        self.is_dask = "dask" in str(df.__class__)
        self._n_rows = df.shape[0]

    @property
    def n_rows(self):
        if hasattr(self._n_rows, "compute"):
            self._n_rows = self._n_rows.compute()
        return self._n_rows

    @staticmethod
    def clean(row):
        out = []
        for v in row:
            if hasattr(v, "compute"):
                v = v.compute()
            if v != v:
                v = None
            elif isinstance(v, (numpy.int8, numpy.int16, numpy.int32, numpy.int64)):
                v = int(v)
            elif isinstance(v, (numpy.float16, numpy.float32, numpy.float64)):
                v = float(v)
                if not math.isfinite(v):
                    v = None
            elif isinstance(v, float) and not math.isfinite(v):
                v = None
            out.append(v)
        return tuple(out)

    def fetch(self, start: int=0, end: int=None):
        """
        Fetch a range of results.  Returns a tuple of:
          (0) - column names
          (1) - An [] of []s, values for each row.
        """
        # for pandas we can use 'iloc' to get our slice
        if not self.is_dask:
            # TODO optimize -- this commented out version may actually be faster, but don't take my word for it
            # rows = json.loads(self.df.to_json(orient="values"))
            rows = list(map(self.clean, self.df.iloc[start:end].itertuples(index=False, name=None)))
            return self.columns, rows
        # special case: entire dataset
        if start == 0 and end is None:
            rows = list(map(self.clean, self.df.itertuples(index=False, name=None)))
            return self.columns, rows
        # support negative range with head() and tail()
        if start < 0:
            return self._fetch_from_end(start, end)
        # one row at a time, optimized for paged forward access
        if self.iter is None:
            self.iter = self.re_iter()
            self.pos = 0
        clean = self.clean
        if start < self.pos:
            self.iter = self.re_iter()
            self.pos = 0
            self.eof = False
        rows = []
        if self.eof:
            return self.columns, rows
        try:
            while self.pos < start:
                next(self.iter)
                self.pos += 1
            while end is None or self.pos < end:
                row = clean(next(self.iter))
                rows.append(row)
                self.pos += 1
        except StopIteration:
            self.eof = True
        return self.columns, rows

    def _fetch_from_end(self, start, end):
        if end is not None and end < 0:
            if end >= start:
                return self.columns, []
            chunk = self.df.tail(-start, compute=False, npartitions=-1)
            chunk = chunk.head(end - start, npartitions=-1)
        else:
            chunk = self.df.tail(-start, npartitions=-1)
        rows = list(map(self.clean, chunk.itertuples(index=False, name=None)))
        return self.columns, rows
