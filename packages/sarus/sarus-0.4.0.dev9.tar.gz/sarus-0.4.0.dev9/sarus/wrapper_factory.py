from typing import Any, Union, cast

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from sarus_data_spec.context import global_context

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.manager.typing import LocalSDKManager


class DataSpecWrapperFactory:
    def __init__(self):
        self.registry = {}

    def register(
        self,
        python_classname: str,
        sarus_wrapper_class: DataSpecWrapper,
    ) -> None:
        self.registry[python_classname] = sarus_wrapper_class

    def create(self, dataspec: st.DataSpec) -> Union[DataSpecWrapper, Any]:
        """Create a wrapper class from a DataSpec.

        If the dataspec's python value is not managed by the SDK, returns an
        unwrapped Python object.
        """
        context = global_context()
        manager: LocalSDKManager = context.manager()
        python_type = manager.python_type(dataspec)
        SarusWrapperClass = self.registry.get(python_type)
        if SarusWrapperClass:
            return SarusWrapperClass.from_dataspec(dataspec)
        else:
            # Datasets are either pd.DataFrame or pd.Series
            if dataspec.prototype() != sp.Scalar:
                raise TypeError(f"Expected a Scalar {dataspec}")
            scalar = cast(st.Scalar, dataspec)
            alt_scalar = scalar.variant(
                kind=st.ConstraintKind.SYNTHETIC, public_context=[]
            )
            return alt_scalar.value()
