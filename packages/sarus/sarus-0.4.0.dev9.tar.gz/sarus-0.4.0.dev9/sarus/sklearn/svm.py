from __future__ import annotations

import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_method, sarus_model

try:
    import sklearn.svm as svm
    from sklearn.svm import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class SVC(DataSpecWrapper[svm.SVC]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_SVC)
    def __init__(self, *args, **kwargs) -> None:
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y, sample_weight=None):
        ...


register_ops()
