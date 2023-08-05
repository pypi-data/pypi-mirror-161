from enum import Enum
from typing import Any, Optional, Protocol, TypeVar, Union, runtime_checkable

import sarus_data_spec.typing as st
from requests import Session


class Client(Protocol):
    session: Session


class SyncPolicy(Enum):
    MANUAL = 0
    SEND_ON_INIT = 1


class DataSpecVariant(Enum):
    USER_DEFINED = "user_defined"
    SYNTHETIC = "synthetic"
    MOCK = "mock"
    ALTERNATIVE = "alternative"


T = TypeVar("T")


@runtime_checkable
class DataSpecWrapper(Protocol[T]):
    def python_type(self) -> Optional[str]:
        ...

    def dataspec(
        self, kind: DataSpecVariant = DataSpecVariant.USER_DEFINED
    ) -> st.DataSpec:
        ...

    def __sarus_eval__(self) -> st.DataSpecValue:
        """Return value of synthetic variant."""
        ...


class DataSpecWrapperFactory(Protocol):
    def register(
        self,
        python_classname: str,
        sarus_wrapper_class: DataSpecWrapper,
    ) -> None:
        ...

    def create(self, dataspec: st.DataSpec) -> Union[DataSpecWrapper, Any]:
        """Create a wrapper class from a DataSpec.

        If the dataspec's python value is not managed by the SDK, returns an
        unwrapped Python object.
        """
        ...
