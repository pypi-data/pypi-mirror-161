from typing import cast

import sarus_data_spec.protobuf as sp
from sarus_data_spec.context.public import Public as PublicContext
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.factory import Factory
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.transform import Transform

# from sarus.storage.local import Storage
from sarus_data_spec.storage.local import Storage

from sarus.dataspec_wrapper import MetaWrapper
from sarus.manager.local_sdk import LocalSDKManager, manager
from sarus.typing import Client
from sarus.wrapper_factory import DataSpecWrapperFactory

from ..typing import SyncPolicy


class LocalSDKContext(PublicContext):
    """A default context"""

    def __init__(self, client: Client) -> None:
        super().__init__()
        self._storage = Storage()  # type:ignore
        self._sync_policy = SyncPolicy.SEND_ON_INIT
        self.client = client
        self._manager = manager(self.storage(), self.client)

        self._dataspec_factory = Factory()
        self.factory().register(
            sp.type_name(sp.Dataset),
            lambda protobuf: Dataset(cast(sp.Dataset, protobuf)),
        )
        self.factory().register(
            sp.type_name(sp.Scalar),
            lambda protobuf: Scalar(cast(sp.Scalar, protobuf)),
        )
        self.factory().register(
            sp.type_name(sp.Transform),
            lambda protobuf: Transform(cast(sp.Transform, protobuf)),
        )

        self._wrapper_factory = DataSpecWrapperFactory()
        for (
            python_classname,
            sarus_wrapper_class,
        ) in MetaWrapper._wrapper_classes:
            self._wrapper_factory.register(
                python_classname=python_classname,
                sarus_wrapper_class=sarus_wrapper_class,
            )

    def factory(self) -> Factory:
        return self._dataspec_factory

    def wrapper_factory(self) -> DataSpecWrapperFactory:
        return self._wrapper_factory

    def storage(self) -> Storage:
        return self._storage

    def manager(self) -> LocalSDKManager:
        return self._manager

    def set_sync_policy(self, policy: SyncPolicy) -> None:
        self._sync_policy = policy

    def sync_policy(self) -> SyncPolicy:
        return self._sync_policy
