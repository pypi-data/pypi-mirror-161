from __future__ import annotations

import inspect
import logging
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    cast,
    get_args,
)

import requests
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from sarus_data_spec.context import global_context
from sarus_data_spec.protobuf.utilities import dict_deserialize
from sarus_data_spec.query_manager.typing import DataspecPrivacyPolicy

from sarus.context.typing import LocalSDKContext
from sarus.utils import register_ops

from .typing import DataSpecVariant, DataSpecWrapper, SyncPolicy

logger = logging.getLogger(__name__)


IGNORE_WARNING = [
    "_ipython_canary_method_should_not_exist_",
]

T = TypeVar("T")


class MetaWrapper(type):
    """Metaclass used to delegate non overriden class attributes to the wrapped
    class."""

    _wrapper_classes: List[Tuple[str, type]] = []

    def __new__(cls, name, bases, dct):
        """Creation of a new DataSpecWrapper class.

        The arguments `name`, `bases` and `dct` are the standard arguments
        passed to the `type` function when creating a new class
        https://docs.python.org/3/library/functions.html#type
        """
        new_wrapper_class = super().__new__(cls, name, bases, dct)

        if name != "DataSpecWrapper":
            # Set the wrapped class from the type annotation
            wrapped_python_class = get_args(
                new_wrapper_class.__orig_bases__[0]
            )[0]
            new_wrapper_class.__wraps__ = wrapped_python_class

            # Register the new class in the wrapper factory
            python_classname = str(wrapped_python_class)
            if python_classname == "~T":
                logger.warning(
                    f"Wrapper class {name} has no associated Python type."
                )
            else:
                MetaWrapper._wrapper_classes.append(
                    (str(wrapped_python_class), new_wrapper_class)
                )

        return new_wrapper_class

    def __getattr__(self, name):
        return getattr(self.__wraps__, name)


class DataSpecWrapper(Generic[T], metaclass=MetaWrapper):
    """This class wraps Sarus DataSpecs objects for the SDK.

    More specifically, it wraps 3 variants of the same DataSpec. These variants
    can be identified with the DataSpecVariant enum:
    - USER_DEFINED: the DataSpec as defined by the user
    - SYNTHETIC: the synthetic variant of the USER_DEFINED DataSpec
    - MOCK: a small sample of the SYNTHETIC variant

    The wrapper has a fallback behavior implemented in the __getattr__ method.
    Any attribute access attempt that is not explicitly catched by a method
    will be delegated to the SYNTHETIC dataspec's value.

    Subclasses such as sarus.pandas.DataFrame must implement the `value` method.
    """

    # This is a class variable hoding all DataSpecWrapper instances
    # This is used by the `dataspec_wrapper_symbols` method.
    instances: Dict[str, int] = dict()

    @classmethod
    def from_dataspec(
        cls, dataspec: st.DataSpec
    ) -> DataSpecWrapper(Generic[T]):
        # because __new__ may be overwritten by init_wrapped decorator
        wrapper = object.__new__(cls)
        wrapper._set_dataspec(dataspec)
        return wrapper

    def _set_dataspec(self, dataspec: st.DataSpec) -> None:
        self._dataspec = dataspec
        self._alt_dataspec = None
        self._alt_policy = None  # The alternative Dataspec's privacy policy

        # This class only works with a LocalSDKContext
        context: LocalSDKContext = global_context()
        assert isinstance(context, LocalSDKContext)
        self._manager = context.manager()
        if context.sync_policy() == SyncPolicy.SEND_ON_INIT:
            self.send_server(execute=True)

        # Register wrapper instance
        DataSpecWrapper.instances[dataspec.uuid()] = id(self)
        DataSpecWrapper.instances[
            self.dataspec(DataSpecVariant.SYNTHETIC).uuid()
        ] = id(self)

    def python_type(self) -> Optional[str]:
        """Return the value's Python type name.

        The LocalSDKManager registers an attribute holding the MOCK value's
        Python type (see `LocalSDKManagerinfer_output_type` method). This is
        used to instantiate the right DataSpecWrapper class e.g. instantiate a
        sarus.pandas.DataFrame if the Python value is a pandas.DataFrame.
        """
        return self._manager.python_type(self)

    def dataspec_wrapper_symbols(
        self, f_locals, f_globals
    ) -> Dict[str, Optional[str]]:
        """Returns the symbols table in the caller's namespace.

        For instance, if the data practitioner defines a DataSpecWrapper using
        the symbol X in his code (e.g. X = dataset.as_pandas()) then the symbol
        table contain the mapping between the DataSpecWrapper instances' ids
        and their symbols. This is used to make the dot representation more
        readable.
        """
        mapping = {
            id(obj): symbol
            for symbol, obj in f_locals.items()
            if isinstance(obj, DataSpecWrapper)
        }
        mapping.update(
            {
                id(obj): symbol
                for symbol, obj in f_globals.items()
                if isinstance(obj, DataSpecWrapper)
            }
        )
        symbols = dict()
        for uuid, _id in DataSpecWrapper.instances.items():
            symbols[uuid] = mapping.get(_id, None)
        return symbols

    def dot(
        self,
        kind: DataSpecVariant = DataSpecVariant.USER_DEFINED,
        remote: bool = True,
    ) -> str:
        """Graphviz's dot representation of the DataSpecWrapper graph.

        Uses color codes to show statuses.

        Args:
            kind (DataSpecVariant): the DataSpec to represent.
            remote (true): Which Manager to inspect.
                If true shows the DataSpec's status on the server,
                else show the DataSpec's status locally.
        """
        ds = self.dataspec(kind)
        caller_frame = inspect.currentframe().f_back
        symbols = self.dataspec_wrapper_symbols(
            caller_frame.f_locals, caller_frame.f_globals
        )
        return self._manager.dot(ds, symbols=symbols, remote=remote)

    def send_server(self, execute: bool = False) -> requests.Response:
        """Send the DataSpec graph to the server.

        The server sends an alternative DataSpec back which is compliant with
        the privacy policy defined for the current user.

        Args:
            execute (bool): If true, tell the server to compute the value.
        """
        dataspec = self.dataspec(kind=DataSpecVariant.USER_DEFINED)
        resp = self._manager._post_dataspec(dataspec, execute=execute)

        resp.raise_for_status()

        # Register the alternative DataSpec
        resp_dict = resp.json()
        alt_protobuf = dict_deserialize(resp_dict["alternative"])
        context: LocalSDKContext = global_context()
        self._alt_dataspec = context.factory().create(alt_protobuf)
        self._alt_policy = resp_dict["policy"]
        DataSpecWrapper.instances[self._alt_dataspec.uuid()] = id(self)

    def delete_from_server(self) -> None:
        """Delete a DataSpec from the server's storage."""
        dataspec = self.dataspec(kind=DataSpecVariant.ALTERNATIVE)
        self._manager._delete_remote(dataspec.uuid())

    def delete_from_local(self) -> None:
        """Delete a DataSpec from the local storage."""
        dataspec = self.dataspec(kind=DataSpecVariant.ALTERNATIVE)
        self._manager._delete_local(dataspec.uuid())

    def __eval_policy__(self) -> str:
        """The alternative dataspec's privacy policy."""
        if self._alt_policy is not None:
            return self._alt_policy
        else:
            return DataspecPrivacyPolicy.DP.value

    def _status(self) -> Dict[str, Any]:
        dataspecs = {
            "user": self.dataspec(kind=DataSpecVariant.USER_DEFINED),
            "alt": self.dataspec(kind=DataSpecVariant.ALTERNATIVE),
            "mock": self.dataspec(kind=DataSpecVariant.MOCK),
        }

        result = {}
        for key, ds in dataspecs.items():
            statuses = self._manager._get_status(ds, remote=True)
            remote_status = [s for s in statuses if s["id"] == ds.uuid()][0]

            statuses = self._manager._get_status(ds, remote=False)
            local_status = [s for s in statuses if s["id"] == ds.uuid()][0]

            result[key] = {
                "remote": remote_status.get("code", "no_status"),
                "local": local_status.get("code", "no_status"),
            }

        return result

    def dataspec(
        self, kind: DataSpecVariant = DataSpecVariant.USER_DEFINED
    ) -> st.DataSpec:
        """Return one of the wrapped DataSpec object."""
        if kind == DataSpecVariant.USER_DEFINED:
            return self._dataspec
        if kind == DataSpecVariant.ALTERNATIVE:
            if self._alt_dataspec:
                return self._alt_dataspec
            else:
                # logger.warning(
                #     "Alternative DataSpec not defined."
                #     " Send DataSpec to server to get an alternative."
                # )
                return self._dataspec.variant(
                    kind=st.ConstraintKind.SYNTHETIC, public_context=[]
                )
        elif kind == DataSpecVariant.SYNTHETIC:
            return self._dataspec.variant(
                kind=st.ConstraintKind.SYNTHETIC, public_context=[]
            )
        elif kind == DataSpecVariant.MOCK:
            return self._manager.mock(self._dataspec)
        else:
            raise ValueError(f"Unknown kind {kind}")

    def __len__(self) -> int:
        logger.info(
            f"`__len__` not supported on {type(self)}, "
            "object has been evaluated for this method. "
            "See Sarus documentation."
        )
        return self.__sarus_eval__().__len__()

    def __repr__(self) -> int:
        return self.__sarus_eval__().__repr__()

    def __iter__(self) -> int:
        return self.__sarus_eval__().__iter__()

    def __float__(self) -> int:
        return self.__sarus_eval__().__float__()

    def __int__(self) -> int:
        return self.__sarus_eval__().__int__()

    def __bool__(self) -> int:
        return self.__sarus_eval__().__bool__()

    def __format__(self, *args, **kwargs) -> int:
        return self.__sarus_eval__().__format__(*args, **kwargs)

    def __sarus_eval__(self) -> T:
        """Return the value of alternative DataSpec's variant."""
        dataspec = self.dataspec(kind=DataSpecVariant.ALTERNATIVE)
        if dataspec.prototype() == sp.Dataset:
            dataset = cast(T, dataspec)
            return dataset.to_pandas()
        else:
            scalar = cast(st.Scalar, dataspec)
            return cast(T, scalar.value())

    def __getattr__(self, name: str) -> Any:
        if name not in IGNORE_WARNING:
            logger.info(
                f"`{name}` not supported on {type(self)}, "
                "object has been evaluated for this method. "
                "See Sarus documentation."
            )
        return self.__sarus_eval__().__getattribute__(name)

    def _ipython_display_(self) -> None:
        display(self.__sarus_eval__())


register_ops()
