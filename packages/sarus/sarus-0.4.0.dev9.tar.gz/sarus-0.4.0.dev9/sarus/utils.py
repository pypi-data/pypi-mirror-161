import inspect
import os
from functools import partial, wraps
from typing import Any, Callable, Dict, Optional, Type

import pandas as pd
import sarus_data_spec.typing as st
import yaml
from sarus_data_spec.config import WHITELISTED_TRANSFORMS
from sarus_data_spec.context import global_context
from sarus_data_spec.scalar import model
from sarus_data_spec.transform import external
from sarus_data_spec.variant_constraint import variant_constraint

from .context.typing import LocalSDKContext
from .typing import DataSpecVariant, DataSpecWrapper

config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_file) as f:
    config = yaml.load(f.read(), Loader=yaml.Loader)


def module_config(module_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the module's configuration from the config dict."""
    keys = module_name.split(".")
    module_conf = config
    for key in keys:
        if module_conf is None:
            return
        module_conf = module_conf.get(key)
    return module_conf


def eval(x: Any) -> st.DataSpecValue:
    if isinstance(x, DataSpecWrapper):
        return x.__sarus_eval__()
    elif isinstance(x, list):
        return [eval(x_) for x_ in x]
    elif isinstance(x, tuple):
        return tuple([eval(x_) for x_ in x])
    elif isinstance(x, dict):
        return {eval(k): eval(v) for k, v in x.items()}
    else:
        return x


def eval_policy(x: Any) -> Optional[str]:
    """The alternative dataspec's privacy policy."""
    if isinstance(x, DataSpecWrapper):
        return x.__eval_policy__()
    else:
        return None


_registered_methods = []
_registered_functions = []


class register_method:
    """This decorator method allows to register methods declared in classes.

    It uses this behavior since Python 3.6
    https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    """

    def __init__(self, method: Callable, code_name: str) -> None:
        self.method = method
        self.code_name = code_name

    def __set_name__(self, owner: Type, name: str) -> None:
        global _registered_methods
        _registered_methods.append(
            (owner.__module__, owner.__name__, name, self.code_name)
        )
        setattr(owner, name, self.method)


def register_ops():
    """Monkey-patching standard libraries to have Sarus functions.

    This functions is intended to be called in a Sarus module. The module's
    local variables will be modified dynamically (monkey patching) to replace
    some functions or methods by Sarus equivalent operations.

    Technically, we get the previous frame's (the module where the function is
    called) locals mapping and update it.

    The modified methods and functions are listed in the `sarus/config.yaml`
    file.
    """
    previous_frame = inspect.currentframe().f_back
    local_vars = previous_frame.f_locals
    module_name = local_vars["__name__"]
    module_conf = module_config(module_name)
    if module_conf is None:
        return

    # Registering module functions
    global _registered_functions
    functions = module_conf.get("sarus_functions", {})
    for fn_name, fn_code_name in functions.items():
        local_vars[fn_name] = create_op(fn_code_name)
        _registered_functions.append((module_name, fn_name, fn_code_name))

    # Registering explicit evaluation functions
    explicit_eval_fns = module_conf.get("explicit_eval", [])
    for fn_name in explicit_eval_fns:
        fn_obj = local_vars[fn_name]
        local_vars[fn_name] = explicit_sarus_eval(fn_obj)

    # Registering classes methods
    global _registered_methods
    classes = module_conf.get("classes", {})
    for class_name, methods in classes.items():
        class_obj = local_vars[class_name]
        for mth_name, mth_code_name in methods.items():
            _registered_methods.append(
                (module_name, class_name, mth_name, mth_code_name)
            )
            setattr(class_obj, mth_name, create_op(mth_code_name))


def _sarus_op(
    code_name: str,
    inplace: bool = False,
    register: bool = False,
    is_property: bool = False,
):
    """Parametrized decorator to register a Sarus external op."""

    def parametrized_wrapper(ops_fn):
        @wraps(ops_fn)
        def wrapper_fn(*args, **kwargs):
            """Some arguments are instances of DataSpecWrapper and others are
            just Python object. This wrapper registers a new dataspec."""
            py_args = {
                i: eval(arg)
                for i, arg in enumerate(args)
                if not isinstance(arg, DataSpecWrapper)
            }
            ds_args_pos = [
                i
                for i, arg in enumerate(args)
                if isinstance(arg, DataSpecWrapper)
            ]
            ds_args = [
                arg.dataspec(DataSpecVariant.USER_DEFINED)
                for arg in args
                if isinstance(arg, DataSpecWrapper)
            ]
            py_kwargs = {
                eval(name): eval(arg)
                for name, arg in kwargs.items()
                if not isinstance(arg, DataSpecWrapper)
            }
            ds_kwargs = {
                name: arg.dataspec(DataSpecVariant.USER_DEFINED)
                for name, arg in kwargs.items()
                if isinstance(arg, DataSpecWrapper)
            }
            transform = external(
                id=code_name,
                py_args=py_args,
                py_kwargs=py_kwargs,
                ds_args_pos=ds_args_pos,
            )
            new_dataspec = transform(*ds_args, **ds_kwargs)
            context: LocalSDKContext = global_context()

            new_dataspec_wrapper = context.wrapper_factory().create(
                new_dataspec
            )

            if inplace:
                self: DataSpecWrapper = args[0]  # TODO check semantic
                self._set_dataspec(new_dataspec)

            return new_dataspec_wrapper

        if is_property:
            wrapper_fn = property(wrapper_fn)

        if register:
            wrapper_fn = register_method(wrapper_fn, code_name)

        return wrapper_fn

    return parametrized_wrapper


sarus_method = partial(_sarus_op, register=True, is_property=False)
sarus_property = partial(_sarus_op, register=True, is_property=True)


def sarus_model(code):
    """Decorator to initialize models."""

    def parametrized_wrapper(ops_fn):
        @wraps(ops_fn)
        def wrapper_fn(self, *args, **kwargs):
            dataspec = model(model_class=code, *args, **kwargs)
            variant_constraint(st.ConstraintKind.PUBLIC, dataspec)
            self._set_dataspec(dataspec)

        wrapper_fn = register_method(wrapper_fn, code)

        return wrapper_fn

    return parametrized_wrapper


def create_op(code_name: str, inplace: bool = False) -> Callable:
    """Create an op function without decorating a function."""

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


@_sarus_op(code_name="std.LEN")
def length(__o: object):
    ...


def explicit_sarus_eval(func):
    """Decorator to explicitly collect Dataspec's values before calling."""

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        args = [eval(arg) for arg in args]
        kwargs = {key: eval(val) for key, val in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped_func


def init_wrapped(wrapper_class):
    """Define the constructor to return a wrapped instance."""
    assert issubclass(wrapper_class, DataSpecWrapper)

    def __new__(cls, *args, **kwargs):
        return wrapper_class.__wraps__(*args, **kwargs)

    wrapper_class.__new__ = staticmethod(__new__)

    return wrapper_class


def generate_op_list():
    """Generate the list of registered operations in a Markdown file.

    NB: This does not list DataspecWrappers without any operations declared.
    """
    global _registered_functions, _registered_methods

    methods = pd.DataFrame.from_records(_registered_methods)
    methods.columns = ["module", "class", "method", "code"]

    functions = pd.DataFrame.from_records(_registered_functions)
    functions.columns = ["module", "function", "code"]

    all_items = methods.append(functions, ignore_index=True)

    lines, whitelisted_lines = [], []
    for mod_name, mod_df in all_items.groupby(by="module"):
        has_whitelisted = False
        mod_whitelisted_lines = []

        lines.append(f"\n# {mod_name}")
        mod_whitelisted_lines.append(f"# {mod_name}")

        fns = (
            mod_df.loc[:, ["function", "code"]]
            .dropna()
            .sort_values(by="function")
        )
        mask = fns.code.apply(lambda x: x in WHITELISTED_TRANSFORMS)
        whitelisted_fns = fns[mask]
        if len(fns) > 0:
            lines.append("\n## Functions")
            lines += list(map(lambda x: f"- `{x}`", fns.function))
        if len(whitelisted_fns) > 0:
            has_whitelisted = True
            mod_whitelisted_lines.append("\n## Functions")
            mod_whitelisted_lines += list(
                map(lambda x: f"- `{x}`", whitelisted_fns.function)
            )

        for class_name, class_df in mod_df.groupby("class"):
            if class_name == "DataSpecWrapper":
                class_name = "Generic Operations"
            lines.append(f"\n## {class_name}")
            methods = (
                class_df.loc[:, ["method", "code"]]
                .dropna()
                .sort_values(by="method")
            )
            mask = methods.code.apply(lambda x: x in WHITELISTED_TRANSFORMS)
            lines += list(map(lambda x: f"- `{x}`", methods.method))

            whitelisted_methods = methods[mask]
            if len(whitelisted_methods) > 0:
                has_whitelisted = True
                mod_whitelisted_lines.append(f"\n## {class_name}")
                mod_whitelisted_lines += list(
                    map(lambda x: f"- `{x}`", whitelisted_methods.method)
                )

        if has_whitelisted:
            whitelisted_lines += mod_whitelisted_lines

    ops = "\n".join(lines)
    whitelisted_ops = "\n".join(whitelisted_lines)

    op_file = os.path.join(os.path.dirname(__file__), "op_list.md")
    with open(op_file, "w") as f:
        f.write(ops)

    whitelisted_op_file = os.path.join(
        os.path.dirname(__file__), "whitelisted_op_list.md"
    )
    with open(whitelisted_op_file, "w") as f:
        f.write(whitelisted_ops)


if __name__ == "__main__":
    generate_op_list()
