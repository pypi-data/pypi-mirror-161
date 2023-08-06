import pyarrow as pa
import pyarrow.compute as pc
import pymsd.proto.dataframe_pb2 as msd
import numpy as np

def to_arrow_array(s : msd.Series) -> pa.Array:
    if s.dtype == msd.FieldKind.Float64:
        return pa.Array.from_buffers(pa.float64(), len(s.datas)/8, [None, pa.py_buffer(s.datas)])
    elif s.dtype == msd.FieldKind.Int64:
        return pa.Array.from_buffers(pa.int64(), len(s.datas)/8, [None, pa.py_buffer(s.datas)])
    elif s.dtype == msd.FieldKind.UInt64:
        return pa.Array.from_buffers(pa.uint64(), len(s.datas)/8, [None, pa.py_buffer(s.datas)])
    elif s.dtype == msd.FieldKind.DateTime:
        return pc.add(pa.Array.from_buffers(pa.int64(), len(s.datas)/8, [None, pa.py_buffer(s.datas)]), 8 * 3600 * 1_000_000_000).cast(pa.timestamp('ns'))
    elif s.dtype == msd.FieldKind.Decimal64:
        a = np.frombuffer(s.datas, '>i8')
        v = a >> 8
        d = 10**((a & 0xFF) >> 4)
        neg = np.where(a & 1 == 1, -1, 1)
        return pa.array(v * neg / d, type=pa.float64())
    elif s.dtype == msd.FieldKind.String:
        return pa.array(s.texts, type=pa.string())
    return None