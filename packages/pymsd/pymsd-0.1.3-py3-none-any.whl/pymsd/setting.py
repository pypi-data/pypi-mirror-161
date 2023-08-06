
_PANDAS_FOUND = True
_PYARROW_FOUND = True
_POLARS_FOUND = True

try:
    import pandas as pd # pragma: no cover
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