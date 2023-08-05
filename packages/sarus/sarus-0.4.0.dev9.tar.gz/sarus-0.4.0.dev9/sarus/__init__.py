"""SDK classes and functions."""
import warnings

import nest_asyncio

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sarus import (
        numpy,
        pandas,
        pandas_profiling,
        plotly,
        sklearn,
        std,
        xgboost,
    )

    from .sarus import Client, Dataset
    from .utils import eval, eval_policy, length

VERSION = "0.4.0.dev9"

__all__ = ["Dataset", "Client", "length", "eval", "eval_policy", "config"]


nest_asyncio.apply()
