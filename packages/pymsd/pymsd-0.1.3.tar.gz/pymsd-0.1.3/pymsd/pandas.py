import pandas as pd
import numpy as np
import pymsd.proto.dataframe_pb2 as msd


def to_pandas_series(s: msd.Series) -> pd.Series:
    """
    convert msd.Series to pandas.Series
    """
    if s.dtype == msd.FieldKind.Float64:
        a = np.frombuffer(s.datas, np.float64)
        return pd.Series(a, name=s.name)
    if s.dtype == msd.FieldKind.Int64:
        a = np.frombuffer(s.datas, np.int64)
        return pd.Series(a, name=s.name)
    if s.dtype == msd.FieldKind.DateTime:
        a = np.frombuffer(s.datas, 'datetime64[ns]')
        a = a + 8 * 3600 * 1_000_000_000
        return pd.Series(a, name=s.name)
    if s.dtype == msd.FieldKind.Decimal64:
        a = np.frombuffer(s.datas, '>i8')
        v = a >> 8
        d = 10**((a & 0xFF) >> 4)
        neg = np.where(a & 1 == 1, -1, 1)
        return pd.Series(v * neg / d, dtype=np.float64, name=s.name)
    if s.dtype == msd.FieldKind.String:
        return pd.Series(s.texts, dtype=str, name=s.name)
    return None


def to_pandas_dataframe(df: msd.DataFrame) -> pd.DataFrame:
    """
    convert msd.DataFrame to pandas.DataFrame
    """
    data = {}
    index = None
    for i, c in enumerate(df.columns):
        if i != df.pk_col:
            data[c.name] = to_pandas_series(c)
        else:
            index = to_pandas_series(c)
    return pd.DataFrame.from_dict(data).set_index(index)
