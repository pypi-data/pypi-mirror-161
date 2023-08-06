from typing import List, Tuple
import numpy as np
import pymsd.proto.dataframe_pb2 as msd

def to_numpy_ndarray(s: msd.Series) -> np.ndarray:
    """
    convert msd.Series to numpy.ndarray
    """
    if s.dtype == msd.FieldKind.Float64:
        return np.frombuffer(s.datas, np.float64)
    if s.dtype == msd.FieldKind.Int64:
        return np.frombuffer(s.datas, np.int64)
    if s.dtype == msd.FieldKind.UInt64:
        return np.frombuffer(s.datas, np.uint64)
    if s.dtype == msd.FieldKind.DateTime:
        a = np.frombuffer(s.datas, 'datetime64[ns]')
        a = a + 8 * 3600 * 1_000_000_000
        return a
    if s.dtype == msd.FieldKind.Decimal64:
        a = np.frombuffer(s.datas, '>i8')
        v = a >> 8
        d = 10**((a & 0xFF) >> 4)
        neg = np.where(a & 1 == 1, -1.0, 1.0)
        return (v.astype(np.float64) * neg / d)
    if s.dtype == msd.FieldKind.String:
        return np.array(s.texts)
    return None

def to_numpy_list(df: msd.DataFrame) -> List[Tuple[str, np.ndarray]]:
    """
    convert msd.DataFrame to a list of named numpy.ndarray
    """
    data = []
    for c in df.columns:
        data.append((c.name, c))
    return data