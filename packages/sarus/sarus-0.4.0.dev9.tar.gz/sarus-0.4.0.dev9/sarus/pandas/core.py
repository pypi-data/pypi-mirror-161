import pandas as pd

from sarus.dataspec_wrapper import DataSpecWrapper


class Index(DataSpecWrapper[pd.Index]):
    ...


class RangeIndex(DataSpecWrapper[pd.RangeIndex]):
    ...


class DataFrameGroupBy(DataSpecWrapper[pd.core.groupby.DataFrameGroupBy]):
    ...
