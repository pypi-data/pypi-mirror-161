import importlib
from pandasbox.sqlite_table import PandasBox


if importlib.util.find_spec("pandas"):
    from pandasbox.pandas_table import PandasBox
