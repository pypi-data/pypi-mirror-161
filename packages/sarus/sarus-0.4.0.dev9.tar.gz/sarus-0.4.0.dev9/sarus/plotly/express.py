from sarus.utils import register_ops

try:
    from plotly.express import *
except ModuleNotFoundError:
    pass
else:
    register_ops()
