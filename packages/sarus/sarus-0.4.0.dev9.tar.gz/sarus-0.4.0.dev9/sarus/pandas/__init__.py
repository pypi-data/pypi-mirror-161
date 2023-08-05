"""Sarus Pandas package documentation."""
from pandas import *

from sarus.utils import register_ops

from .core import *
from .dataframe import DataFrame, Series

register_ops()
