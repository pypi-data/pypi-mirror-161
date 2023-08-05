"""Sarus Tensorflow package documentation."""
from sarus.utils import register_ops

try:
    from .xgboost import XGBClassifier
except NameError:
    pass
else:
    __all__ = ["XGBClassifier"]

    register_ops()
