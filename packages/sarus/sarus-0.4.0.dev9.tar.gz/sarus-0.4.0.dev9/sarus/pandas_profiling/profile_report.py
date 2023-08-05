from sarus_data_spec.transform import external

import sarus.pandas as spd
from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.typing import DataSpecVariant
from sarus.utils import register_ops

try:
    import pandas_profiling
except ModuleNotFoundError:
    pass


class ProfileReport(DataSpecWrapper[pandas_profiling.ProfileReport]):
    def __init__(self, df=None, **kwargs) -> None:
        if not isinstance(df, spd.DataFrame):
            raise TypeError("df is not an instance of sarus.pandas.DataFrame.")

        parent_dataspec = df.dataspec(kind=DataSpecVariant.USER_DEFINED)
        dataspec = external(
            "pandas_profiling.PD_PROFILE_REPORT",
            py_kwargs=kwargs,
            py_args={},
            ds_args_pos=[0],
        )(parent_dataspec)
        self._set_dataspec(dataspec)


register_ops()
