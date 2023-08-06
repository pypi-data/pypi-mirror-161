import pymsd.proto.dataframe_pb2 as msd

_NUMPY_FOUND = True
_PYARROW_FOUND = True
_POLARS_FOUND = True

try:
    import numpy as np # pragma: no cover
except ImportError:
    _PANDAS_FOUND = False

try:
    import pyarrow as pa # pragma: no cover
except ImportError:
    _PYARROW_FOUND = False

try:
    import polars as pl # pragma: no cover
except ImportError:
    _POLARS_FOUND = False

def to_polars_series(s: msd.Series) -> pl.Series:
    pass

def to_polars_dataframe(df: msd.DataFrame) -> pl.DataFrame:
    """
    convert msd.DataFrame to pandas.DataFrame
    """
    C = None
    if _PYARROW_FOUND:
        import pymsd.pyarrow
        C = pymsd.pyarrow.to_arrow_array
    elif _NUMPY_FOUND:
        import pymsd.numpy
        C = pymsd.numpy.to_numpy_ndarray
    else:
        C = to_polars_series

    data = {}
    for _i, c in enumerate(df.columns):
        data[c.name] = C(c)
    return pl.DataFrame(data)
