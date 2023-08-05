from enum import Enum
from typing import Protocol, runtime_checkable

from sarus_data_spec.context.typing import Context

from sarus.typing import DataSpecWrapperFactory


@runtime_checkable
class LocalSDKContext(Context, Protocol):
    def wrapper_factory(self) -> DataSpecWrapperFactory:
        ...
