from importlib import import_module

from numpy import *
from numpy import abs

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import init_wrapped, register_ops

from .scalars import *

random = import_module("sarus.numpy.random")


@init_wrapped
class ndarray(DataSpecWrapper[np.ndarray]):
    ...


register_ops()
