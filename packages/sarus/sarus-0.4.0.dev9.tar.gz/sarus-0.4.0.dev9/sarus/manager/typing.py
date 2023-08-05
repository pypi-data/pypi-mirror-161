from typing import Optional, Protocol

import sarus_data_spec.typing as st
from sarus_data_spec.manager.typing import Manager


class LocalSDKManager(Manager, Protocol):
    def mock(self, dataspec: st.DataSpec) -> st.DataSpec:
        """Returns a mock version of a DataSpec.

        This is a kind of compilation used by this manager to infer the DataSpec type and Python type of an external transform's result.
        """
        ...

    def register_source_mock(self, dataspec: st.DataSpec) -> st.DataSpec:
        """Define what a mock is for source or fetched DataSpecs."""
        ...

    def python_type(self, dataspec: st.DataSpec) -> Optional[str]:
        ...
