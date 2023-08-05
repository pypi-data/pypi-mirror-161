from __future__ import annotations

import numpy as np
import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_method, sarus_model

try:
    from sklearn import cluster
    from sklearn.cluster import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class AffinityPropagation(DataSpecWrapper[cluster.AffinityPropagation]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_AFFINITY_PROPAGATION)
    def __init__(
        self,
        *,
        damping=0.5,
        max_iter=200,
        convergence_iter=15,
        copy=True,
        preference=None,
        affinity="euclidean",
        verbose=False,
        random_state="warn",
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class AgglomerativeClustering(
    DataSpecWrapper[cluster.AgglomerativeClustering]
):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_AGGLOMERATIVE_CLUSTERING)
    def __init__(
        self,
        n_clusters=2,
        *,
        affinity="euclidean",
        memory=None,
        connectivity=None,
        compute_full_tree="auto",
        linkage="ward",
        distance_threshold=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class Birch(DataSpecWrapper[cluster.Birch]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_BIRCH)
    def __init__(
        self,
        *,
        threshold=0.5,
        branching_factor=50,
        n_clusters=3,
        compute_labels=True,
        copy=True,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class DBSCAN(DataSpecWrapper[cluster.DBSCAN]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_DBSCAN)
    def __init__(
        self,
        eps=0.5,
        *,
        min_samples=5,
        metric="euclidean",
        metric_params=None,
        algorithm="auto",
        leaf_size=30,
        p=None,
        n_jobs=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class FeatureAgglomeration(DataSpecWrapper[cluster.FeatureAgglomeration]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_AFFINITY_PROPAGATION)
    def __init__(
        self,
        n_clusters=2,
        *,
        affinity="euclidean",
        memory=None,
        connectivity=None,
        compute_full_tree="auto",
        linkage="ward",
        ooling_func=np.mean,
        distance_threshold=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class KMeans(DataSpecWrapper[cluster.KMeans]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_KMEANS)
    def __init__(
        self,
        n_clusters=8,
        *,
        init="k-means++",
        n_init=10,
        max_iter=300,
        tol=0.0001,
        precompute_distances="deprecated",
        verbose=0,
        random_state=None,
        copy_x=True,
        n_jobs="deprecated",
        algorithm="auto",
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class MiniBatchKMeans(DataSpecWrapper[cluster.MiniBatchKMeans]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_MINIBATCH_KMEANS)
    def __init__(
        self,
        n_clusters=8,
        *,
        init="k-means++",
        max_iter=100,
        batch_size=100,
        verbose=0,
        compute_labels=True,
        random_state=None,
        tol=0.0,
        max_no_improvement=10,
        init_size=None,
        n_init=3,
        reassignment_ratio=0.01,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class MeanShift(DataSpecWrapper[cluster.MeanShift]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_MEAN_SHIFT)
    def __init__(
        self,
        *,
        bandwidth=None,
        seeds=None,
        bin_seeding=False,
        min_bin_freq=1,
        cluster_all=True,
        n_jobs=None,
        max_iter=300,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class OPTICS(DataSpecWrapper[cluster.OPTICS]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_OPTICS)
    def __init__(
        self,
        *,
        min_samples=5,
        max_eps=np.inf,
        metric="minkowski",
        p=2,
        metric_params=None,
        cluster_method="xi",
        eps=None,
        xi=0.05,
        predecessor_correction=True,
        min_cluster_size=None,
        algorithm="auto",
        leaf_size=30,
        n_jobs=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class SpectralClustering(DataSpecWrapper[cluster.SpectralClustering]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_SPECTRAL_CLUSTERING)
    def __init__(
        self,
        n_clusters=8,
        *,
        eigen_solver=None,
        n_components=None,
        random_state=None,
        n_init=10,
        gamma=1.0,
        affinity="rbf",
        n_neighbors=10,
        eigen_tol=0.0,
        assign_labels="kmeans",
        degree=3,
        coef0=1,
        kernel_params=None,
        n_jobs=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class SpectralBiclustering(DataSpecWrapper[cluster.SpectralBiclustering]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_SPECTRAL_BICLUSTERING)
    def __init__(
        self,
        n_clusters=3,
        *,
        method="bistochastic",
        n_components=6,
        n_best=3,
        svd_method="randomized",
        n_svd_vecs=None,
        mini_batch=False,
        init="k-means++",
        n_init=10,
        n_jobs="deprecated",
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class SpectralCoclustering(DataSpecWrapper[cluster.SpectralCoclustering]):
    @sarus_model(sp.Scalar.Model.ModelClass.SK_AFFINITY_PROPAGATION)
    def __init__(
        self,
        n_clusters=3,
        *,
        svd_method="randomized",
        n_svd_vecs=None,
        mini_batch=False,
        init="k-means++",
        n_init=10,
        n_jobs="deprecated",
        random_state=None,
        _dataspec=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


register_ops()
