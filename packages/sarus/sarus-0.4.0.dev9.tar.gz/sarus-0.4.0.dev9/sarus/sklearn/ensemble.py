from __future__ import annotations

import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_method, sarus_model

try:
    import sklearn.ensemble as ensemble
    from sklearn.ensemble import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class AdaBoostClassifier(DataSpecWrapper[ensemble.AdaBoostClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_ADABOOST_CLASSIFIER)
    def __init__(
        self,
        base_estimator=None,
        *,
        n_estimators=50,
        learning_rate=1.0,
        algorithm="SAMME.R",
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class AdaBoostRegressor(DataSpecWrapper[ensemble.AdaBoostRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_ADABOOST_REGRESSOR)
    def __init__(
        self,
        base_estimator=None,
        *,
        n_estimators=50,
        learning_rate=1.0,
        loss="linear",
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class BaggingClassifier(DataSpecWrapper[ensemble.BaggingClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_BAGGING_CLASSIFIER)
    def __init__(
        self,
        base_estimator=None,
        n_estimators=10,
        *,
        max_samples=1.0,
        max_features=1.0,
        bootstrap=True,
        bootstrap_features=False,
        oob_score=False,
        warm_start=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class BaggingRegressor(DataSpecWrapper[ensemble.BaggingRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_BAGGING_REGRESSOR)
    def __init__(
        self,
        base_estimator=None,
        *,
        n_estimators=50,
        learning_rate=1.0,
        loss="linear",
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class ExtraTreesClassifier(DataSpecWrapper[ensemble.ExtraTreesClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_EXTRA_TREES_CLASSIFIER)
    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="gini",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features="sqrt",
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        bootstrap=False,
        oob_score=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        class_weight=None,
        ccp_alpha=0.0,
        max_samples=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class ExtraTreesRegressor(DataSpecWrapper[ensemble.ExtraTreesRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_EXTRA_TREES_REGRESSOR)
    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="squared_error",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features=1.0,
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        bootstrap=False,
        oob_score=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        ccp_alpha=0.0,
        max_samples=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class GradientBoostingClassifier(
    DataSpecWrapper[ensemble.GradientBoostingClassifier]
):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_GRADIENT_BOOSTING_CLASSIFIER)
    def __init__(
        self,
        *,
        loss="log_loss",
        learning_rate=0.1,
        n_estimators=100,
        subsample=1.0,
        criterion="friedman_mse",
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_depth=3,
        min_impurity_decrease=0.0,
        init=None,
        random_state=None,
        max_features=None,
        verbose=0,
        max_leaf_nodes=None,
        warm_start=False,
        validation_fraction=0.1,
        n_iter_no_change=None,
        tol=0.0001,
        ccp_alpha=0.0,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class GradientBoostingRegressor(
    DataSpecWrapper[ensemble.GradientBoostingRegressor]
):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_GRADIENT_BOOSTING_REGRESSOR)
    def __init__(
        self,
        *,
        loss="squared_error",
        learning_rate=0.1,
        n_estimators=100,
        subsample=1.0,
        criterion="friedman_mse",
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_depth=3,
        min_impurity_decrease=0.0,
        init=None,
        random_state=None,
        max_features=None,
        alpha=0.9,
        verbose=0,
        max_leaf_nodes=None,
        warm_start=False,
        validation_fraction=0.1,
        n_iter_no_change=None,
        tol=0.0001,
        ccp_alpha=0.0,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class IsolationForest(DataSpecWrapper[ensemble.IsolationForest]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_ISOLATION_FOREST)
    def __init__(
        self,
        *,
        n_estimators=100,
        max_samples="auto",
        contamination="auto",
        max_features=1.0,
        bootstrap=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class RandomForestClassifier(DataSpecWrapper[ensemble.RandomForestClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_RANDOM_FOREST_CLASSIFIER)
    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="gini",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features="sqrt",
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        bootstrap=True,
        oob_score=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        class_weight=None,
        ccp_alpha=0.0,
        max_samples=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...

    @sarus_method("sklearn.SK_PREDICT")
    def predict(self, X):
        ...


class RandomForestRegressor(DataSpecWrapper[ensemble.RandomForestRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_RANDOM_FOREST_REGRESSOR)
    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="squared_error",
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features=1.0,
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        bootstrap=False,
        oob_score=False,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        ccp_alpha=0.0,
        max_samples=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class RandomTreesEmbedding(DataSpecWrapper[ensemble.RandomTreesEmbedding]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_RANDOM_TREES_EMBEDDING)
    def __init__(
        self,
        n_estimators=100,
        *,
        max_depth=5,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        sparse_output=True,
        n_jobs=None,
        random_state=None,
        verbose=0,
        warm_start=False,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class StackingClassifier(DataSpecWrapper[ensemble.StackingClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_STACKING_CLASSIFIER)
    def __init__(
        self,
        estimators,
        final_estimator=None,
        *,
        cv=None,
        stack_method="auto",
        n_jobs=None,
        passthrough=False,
        verbose=0,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class StackingRegressor(DataSpecWrapper[ensemble.StackingRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_STACKING_REGRESSOR)
    def __init__(
        self,
        estimators,
        final_estimator=None,
        *,
        cv=None,
        stack_method="auto",
        n_jobs=None,
        passthrough=False,
        verbose=0,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class VotingClassifier(DataSpecWrapper[ensemble.VotingClassifier]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_VOTING_CLASSIFIER)
    def __init__(
        self,
        estimators,
        *,
        voting="hard",
        weights=None,
        n_jobs=None,
        flatten_transform=True,
        verbose=False,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class VotingRegressor(DataSpecWrapper[ensemble.VotingRegressor]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_VOTING_REGRESSOR)
    def __init__(
        self,
        estimators,
        *,
        weights=None,
        n_jobs=None,
        verbose=False,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class HistGradientBoostingClassifier(
    DataSpecWrapper[ensemble.HistGradientBoostingClassifier]
):
    @sarus_model(
        sp.Scalar.Model.ModelClass.SK_HIST_GRADIENT_BOOSTING_CLASSIFIER
    )
    def __init__(
        self,
        loss="log_loss",
        *,
        learning_rate=0.1,
        max_iter=100,
        max_leaf_nodes=31,
        max_depth=None,
        min_samples_leaf=20,
        l2_regularization=0.0,
        max_bins=255,
        categorical_features=None,
        monotonic_cst=None,
        warm_start=False,
        early_stopping="auto",
        scoring="loss",
        validation_fraction=0.1,
        n_iter_no_change=10,
        tol=1e-07,
        verbose=0,
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method(
        "sklearn.SK_FIT",
        inplace=True,
    )
    def fit(self, X, y=None):
        ...


class HistGradientBoostingRegressor(
    DataSpecWrapper[ensemble.HistGradientBoostingRegressor]
):
    @sarus_model(
        sp.Scalar.Model.ModelClass.SK_HIST_GRADIENT_BOOSTING_REGRESSOR
    )
    def __init__(
        self,
        estimators,
        *,
        weights=None,
        n_jobs=None,
        verbose=False,
        _dataspec=None,
    ):
        ...

    @sarus_method(
        "sklearn.SK_FIT",
        inplace=True,
    )
    def fit(self, X, y=None):
        ...


register_ops()
