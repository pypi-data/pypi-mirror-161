import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_model

try:
    import sklearn.model_selection as sk_model_selection
    from sklearn.model_selection import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class RepeatedStratifiedKFold(
    DataSpecWrapper[sk_model_selection.RepeatedStratifiedKFold]
):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_REPEATED_STRATIFIED_KFOLD)
    def __init__(
        self,
        *,
        n_splits=5,
        n_repeats=10,
        random_state=None,
        _dataspec=None,
    ):
        ...


class KFold(DataSpecWrapper[sk_model_selection.KFold]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_KFOLD)
    def __init__(self, n_splits=5, *, shuffle=False, random_state=None):
        ...


register_ops()
