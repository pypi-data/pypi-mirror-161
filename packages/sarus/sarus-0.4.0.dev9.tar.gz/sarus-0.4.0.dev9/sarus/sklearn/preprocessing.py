import numpy as np
import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_method, sarus_model

try:
    import sklearn.preprocessing as sk_preprocessing
    from sklearn.preprocessing import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class OneHotEncoder(DataSpecWrapper[sk_preprocessing.OneHotEncoder]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_ONEHOT)
    def __init__(
        self,
        *,
        categories="auto",
        drop=None,
        sparse=True,
        dtype=np.float64,
        handle_unknown="error",
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class LabelEncoder(DataSpecWrapper[sk_preprocessing.LabelEncoder]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_LABEL_ENCODER)
    def __init__(
        self,
        *,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, y):
        ...


register_ops()
