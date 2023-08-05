from __future__ import annotations

import asyncio
import io
import logging
import os
import pickle as pkl
import tempfile
from functools import reduce
from http import HTTPStatus
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st
from pyexpat.errors import codes
from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.constants import CACHE
from sarus_data_spec.dataset import transformed
from sarus_data_spec.manager.asyncio import (
    BaseAsyncManager,
    DataSpecErrorStatus,
    StatusAwareComputation,
)
from sarus_data_spec.manager.asyncio.utils import async_iter
from sarus_data_spec.manager.ops.asyncio.processor.routing import (
    transformed_dataset_arrow,
    transformed_scalar,
)
from sarus_data_spec.manager.ops.asyncio.source.sklearn import create_model
from sarus_data_spec.status import last_status
from sarus_data_spec.storage.typing import Storage
from sarus_data_spec.transform import sample, synthetic

import sarus.manager.ops.api as api_ops
from sarus.typing import Client

T = TypeVar("T")

logger = logging.getLogger(__name__)


class FetchOrCompute(StatusAwareComputation[T]):
    """The SDK Manager has to decide wether to fetch the DataSpec's value from
    the server or whether to compute it locally. The implicit rule is to compute
    the DataSpec locally if the DataSpec is not on the server.

    It is the SDK's job to send a DataSpec to the server or not. For instance,
    MOCK DataSpecs are not sent on the server by the SDK, their values will
    therefore be computed locally. On the other side, SYNTHETIC DataSpecs are
    sent on the server, their values will be fetched from the server.
    """

    @classmethod
    def get_status(cls, dataspec: st.DataSpec) -> Dict[str, Any]:
        """Return a dataspec's remote status dict."""
        manager: LocalSDKManager = dataspec.manager()
        resp = api_ops.get_dataspec_status(
            client=manager.sdk_client, dataspecs=[dataspec]
        )
        statuses = resp.json()["items"]
        assert len(statuses) == 1
        (status,) = statuses
        return status

    @classmethod
    async def poll_status(cls, dataspec: st.DataSpec) -> Dict[str, Any]:
        """Poll a dataspec's remote status until processing is finished."""
        status = cls.get_status(dataspec)
        while status["status"] == HTTPStatus.OK and status["code"] in [
            "processing",
            "pending",
        ]:
            # TODO implement timeout
            await asyncio.sleep(1)
            status = cls.get_status(dataspec)
        return status

    @classmethod
    async def fetch(
        cls,
        dataspec: st.Dataset,
        *args,
        **kwargs,
    ) -> T:
        """Fetch DataSpec's value from server."""
        raise NotImplementedError("fetch")

    @classmethod
    async def compute_locally(
        cls,
        dataspec: st.Dataset,
        *args,
        **kwargs,
    ) -> T:
        """Compute DataSpec's value locally."""
        raise NotImplementedError("compute_locally")

    @classmethod
    async def __process__(
        cls,
        dataspec: st.Dataset,
        *args,
        **kwargs,
    ) -> T:
        status = await cls.poll_status(dataspec)

        if status["status"] == HTTPStatus.NOT_FOUND:
            return await cls.compute_locally(dataspec, *args, **kwargs)
        elif status["status"] == HTTPStatus.OK and status["code"] == "ready":
            return await cls.fetch(dataspec, *args, **kwargs)

        # Other cases
        elif status["status"] == HTTPStatus.METHOD_NOT_ALLOWED:
            raise TypeError(f"{dataspec} is not a DataSpec.")

        elif status["status"] == HTTPStatus.OK and status["code"] == "error":
            raise DataSpecErrorStatus(
                f"The Dataspec {dataspec.uuid()} is on the server but has "
                f"an error status {status['message']}"
            )
        elif (
            status["status"] == HTTPStatus.OK and status["code"] == "no_status"
        ):
            raise DataSpecErrorStatus(
                f"The Dataspec {dataspec.uuid()} is on the server "
                "but has no status. Try deleting it from the server."
            )
        else:
            raise NotImplementedError(f"FetchOrCompute uncaught case {status}")


class ToArrowFetchOrCompute(FetchOrCompute[AsyncIterator[pa.RecordBatch]]):
    """SDK's implementation of Manager.async_to_arrow.

    The memory format for arrow is Iterator[pa.RecordBatch]. The cache format
    for arrow is parquet.
    """

    @classmethod
    async def __read_from_cache__(
        cls, dataspec: st.DataSpec, status: st.Status
    ) -> AsyncIterator[pa.RecordBatch]:
        """Write PyArrow batches from a Parquet file."""
        cache_path = cls.cache_path(status)
        table = pq.read_table(source=cache_path)
        batches = table.to_batches()
        return async_iter(batches)

    @classmethod
    async def __write_to_cache__(
        cls, dataspec: st.DataSpec, data: AsyncIterator[pa.RecordBatch]
    ) -> None:
        """Save PyArrow batches as a Parquet file."""
        cache_dir = dataspec.manager().parquet_dir()
        cache_path = os.path.join(cache_dir, f"{dataspec.uuid()}.parquet")
        batches = [batch async for batch in data]
        pq.write_table(
            table=pa.Table.from_batches(batches),
            where=cache_path,
            version="2.6",
        )
        return cache_path, async_iter(batches)

    @classmethod
    async def fetch(
        cls,
        dataspec: st.Dataset,
        batch_size: int,
    ) -> AsyncIterator[pa.RecordBatch]:
        """Fetch DataSpec's value from server."""
        manager: LocalSDKManager = dataspec.manager()
        generator = api_ops.get_dataspec(
            client=manager.sdk_client, dataspec=dataspec
        )
        buffer = io.BytesIO()
        for data in generator:
            buffer.write(data)
        buffer.seek(0)
        return async_iter(
            pq.read_table(buffer).to_batches(max_chunksize=batch_size)
        )

    @classmethod
    async def compute_locally(
        cls,
        dataspec: st.Dataset,
        batch_size: int,
    ) -> AsyncIterator[pa.RecordBatch]:
        """Comoute DataSpec's value locally."""
        if dataspec.is_transformed():
            return await transformed_dataset_arrow(
                dataspec, batch_size=batch_size
            )
        else:
            raise NotImplementedError("ToArrowComputation")


ScalarValue = Any


class ValueFetchOrCompute(FetchOrCompute[ScalarValue]):
    """SDK's implementation of Manager.async_value.

    A Scalar value can be any Python object. The chosen cache format is pickle.
    """

    @classmethod
    async def __read_from_cache__(
        cls, dataspec: st.DataSpec, status: st.Status
    ) -> Any:
        cache_path = cls.cache_path(status)
        with open(cache_path, "rb") as f:
            data = pkl.load(f)
        return data

    @classmethod
    async def __write_to_cache__(
        cls, dataspec: st.DataSpec, data: ScalarValue
    ) -> None:
        cache_dir = dataspec.manager().parquet_dir()
        cache_path = os.path.join(cache_dir, f"{dataspec.uuid()}.pkl")
        with open(cache_path, "wb") as f:
            pkl.dump(data, f)
        return cache_path, data

    @classmethod
    async def compute_locally(cls, dataspec: st.Scalar) -> ScalarValue:
        if dataspec.is_model():
            return await create_model(dataspec)
        elif dataspec.is_transformed():
            return await transformed_scalar(dataspec)
        else:
            raise NotImplementedError("ValueComputation")

    @classmethod
    async def fetch(cls, dataspec: st.Scalar) -> ScalarValue:
        # Fetch from server
        manager: LocalSDKManager = dataspec.manager()
        generator = api_ops.get_dataspec(
            client=manager.sdk_client, dataspec=dataspec
        )
        buffer = io.BytesIO()
        for data in generator:
            buffer.write(data)
        buffer.seek(0)
        return pkl.load(buffer)


class LocalSDKManager(BaseAsyncManager):
    """The Manager of the SDK running on the client side.

    This Manager has two additional functionalities compared to the Base
    manager.

    First, it manages the relationship with the remote server. The
    `computation_graph` method retrieves all objects needed to describe a
    DataSpec. The `_post_dataspec` sends a computation graph to the server. The
    `_get_status` method asks the server for the Statuses of all DataSpecs in a
    target DataSpec's computation graph. The `_delete_remote` method deletes a
    DataSpec from the remote server storage and all related objects so that the
    DB remains in a consistent state.

    The Manager has to handle handle the duality of the local
    storage and the remote storage. The `_get_status` method either fetches the
    status from the local storage or asks the remote server. Computing a
    DataSpec's value can be done locally or requested from the server. This
    decision is made at the StatusAwareComputation level.

    Second, this Managers defines a MOCK version for every DataSpec. The MOCK
    is defined as a smaller version of a DataSpec. In practice, it is a sample
    of SYNTHETIC at the source and MOCKs of transformed DataSpecs are the
    transformed of the MOCKs.

    The MOCK is created and its value computed in the `infer_output_type`
    method. This serves two purposes. First, it provides immediate feedback to
    the user in case of erroneous computation. Second, it allows identifying
    the MOCK's value Python type which is then used by the SDK to instantiate
    the correct DataSpecWrapper type (e.g. instantiate a sarus.pandas.DataFrame
    if the value is a pandas.DataFrame).
    """

    def __init__(
        self,
        storage: Storage,
        protobuf: sp.Manager,
        sdk_client: Client,
    ):
        super().__init__(storage=storage, protobuf=protobuf)
        self._parquet_dir = os.path.join(tempfile.mkdtemp(), "sarus_dataspec")
        os.makedirs(self._parquet_dir, exist_ok=True)
        self.sdk_client = sdk_client

    def _post_dataspec(
        self, dataspec: st.DataSpec, execute: bool = False
    ) -> requests.Response:
        """Send a DataSpec's computation graph to the remote Manager."""
        computation_graph = self.computation_graph(dataspec)
        return api_ops.post_graph(
            client=self.sdk_client,
            target=dataspec,
            dataspecs=computation_graph["dataspecs"],
            transforms=computation_graph["transforms"],
            attributes=computation_graph["attributes"],
            execute=execute,
        )

    def _get_status(
        self, dataspec: st.DataSpec, remote: bool = True
    ) -> List[Dict[str, Any]]:
        """Get a DataSpec's computation graph statuses.

        Args:
            dataset (st.DataSpec): the target DataSpec.
            remote (bool): If true, get the statuses on the server.
        """
        computation_graph = self.computation_graph(dataspec)
        if remote:
            resp = api_ops.get_dataspec_status(
                client=self.sdk_client,
                dataspecs=computation_graph["dataspecs"],
            )
            resp.raise_for_status()
            return resp.json()["items"]
        else:
            statuses = []
            for dataspec in computation_graph["dataspecs"]:
                status = last_status(dataspec, task=CACHE)
                if not status:
                    code = "no_status"
                    message = None
                else:
                    code = status.task(CACHE).stage()
                    message = status.protobuf().properties.get("message")
                statuses.append(
                    {
                        "status": HTTPStatus.OK,
                        "id": dataspec.uuid(),
                        "code": code,
                        "message": message,
                    }
                )
            return statuses

    def _delete_remote(self, uuid: str) -> requests.Response:
        """Delete a DataSpec and referring items on the server."""
        return api_ops.delete_dataspec(client=self.sdk_client, uuid=uuid)

    def _delete_local(self, uuid: str) -> None:
        """Delete a DataSpec locally. MOCKs also have to be deleted."""
        would_delete = self.storage().all_referrings(uuid)
        additional_cleanup = []
        for uuid in would_delete:
            item = self.storage().referrable(uuid)
            if item.prototype() in [sp.Dataset, sp.Scalar]:
                try:
                    mock = self.mock(item)
                except Exception:
                    pass
                else:
                    if mock:
                        additional_cleanup.append(mock)

        self.storage().delete(uuid)
        for item in additional_cleanup:
            self.storage().delete(item.uuid())

    async def async_value(self, scalar: st.Scalar) -> st.DataSpecValue:
        return await ValueFetchOrCompute.accept(dataspec=scalar)

    async def async_to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> AsyncIterator[pa.RecordBatch]:
        return await ToArrowFetchOrCompute.accept(
            dataspec=dataset, batch_size=batch_size
        )

    def mock(self, dataspec: st.DataSpec) -> st.DataSpec:
        """Returns a MOCK version of a DataSpec.

        This is a kind of compilation used by this manager to infer the
        DataSpec's type and Python type of an external transform's result.
        """
        attributes = self.storage().referring(
            dataspec, type_name=sp.type_name(sp.Attribute)
        )
        mock_uuids = [
            att.properties()["mock"]
            for att in attributes
            if "mock" in att.properties()
        ]

        if len(mock_uuids) == 0:
            if dataspec.is_transformed() and not self.is_remote(dataspec):
                # The mock should have been registered
                # when applying the transform
                raise LookupError(
                    "No Mock DataSpec found for a transformed DataSpec"
                )
            else:
                return self.register_source_mock(dataspec)

        elif len(mock_uuids) > 1:
            raise LookupError("More than one mock DataSpec found.")

        (mock_uuid,) = mock_uuids
        mock = cast(st.DataSpec, self.storage().referrable(mock_uuid))
        if mock is None:
            raise LookupError(
                f"Mock {mock_uuid} for dataspec {dataspec.uuid()} "
                "not in Storage."
            )
        return mock

    def register_source_mock(self, dataspec: st.DataSpec) -> st.DataSpec:
        """Define what a mock is for source or fetched DataSpecs."""
        assert not dataspec.is_transformed() or self.is_remote(dataspec)

        if dataspec.prototype() == sp.Scalar:
            scalar = cast(st.Scalar, dataspec)
            assert scalar.is_model()
            mock: st.DataSpec = scalar

        elif dataspec.prototype() == sp.Dataset:
            dataset = cast(st.Dataset, dataspec)
            assert dataset.is_remote()

            # We call transformed() directly specifying the dataspec_type to
            # avoid going through infer_output_type again
            syn_variant = dataset.variant(
                kind=st.ConstraintKind.SYNTHETIC, public_context=[]
            )

            mock = transformed(
                sample(fraction_size=1000),
                *[syn_variant],
                dataspec_type=sp.type_name(sp.Dataset),
            )

        else:
            raise TypeError(f"{dataspec.prototype()} not a DataSpec.")

        self.attach_mock(dataspec, mock)
        return mock

    def attach_mock(self, dataspec: st.DataSpec, mock: st.DataSpec) -> None:
        """The link between a DataSpec and its MOCK is in an attribute."""
        attach_properties(dataspec, properties={"mock": mock.uuid()})

    def attach_python_type(
        self, dataspec: st.DataSpec, python_type: str
    ) -> None:
        """The Python type is stored in an attribute."""
        attach_properties(dataspec, properties={"python_type": python_type})

    def python_type(self, dataspec: st.DataSpec) -> Optional[str]:
        attributes = self.storage().referring(
            dataspec, type_name=sp.type_name(sp.Attribute)
        )
        all_attributes: Dict[str, str] = reduce(
            lambda x, y: {**x, **y},
            map(lambda x: x.properties(), attributes),
            dict(),
        )
        return all_attributes.get("python_type", None)

    def infer_output_type(
        self,
        transform: st.Transform,
        *arguments: st.DataSpec,
        **named_arguments: st.DataSpec,
    ) -> Tuple[str, Callable[[st.DataSpec], None]]:
        """Infer the transform output type: Dataset or Scalar.

        For external transforms, the MOCK value is computed here and the
        value's Python type is attached to the output DataSpec.
        """

        if transform.is_external():
            # Get parent DataSpecs mock DataSpecs
            mock_args = [self.mock(arg) for arg in arguments]
            named_mock_args = {
                name: self.mock(arg) for name, arg in named_arguments.items()
            }
            # Create a temporary mock that we set as a Scalar
            temporary_mock = transformed(
                transform,
                *mock_args,
                dataspec_type=sp.type_name(sp.Scalar),
                dataspec_name="temporary_mock",
                **named_mock_args,
            )
            self.storage().delete(temporary_mock.uuid())
            self._delete_remote(temporary_mock.uuid())

            try:
                mock_value = self.value(temporary_mock)
            except Exception as e:
                raise e
            finally:
                self.storage().delete(temporary_mock.uuid())

            # Infer output types
            python_type = str(type(mock_value))
            dataset_types = [pd.DataFrame]
            dataspec_type = (
                sp.type_name(sp.Dataset)
                if type(mock_value) in dataset_types
                else sp.type_name(sp.Scalar)
            )

            mock: st.DataSpec = transformed(
                transform,
                *mock_args,
                dataspec_type=dataspec_type,
                **named_mock_args,
            )

            # Create the callback
            def attach_info(ds: st.DataSpec) -> None:
                """Attach the mock to the DataSpec"""
                self.attach_mock(ds, mock)
                self.attach_python_type(ds, python_type)

            # Return the output type
            return dataspec_type, attach_info

        elif transform.protobuf().spec.HasField("synthetic"):

            def attach_info(ds: st.DataSpec) -> None:
                mock = transformed(
                    sample(fraction_size=100),
                    *[ds],
                    dataspec_type=sp.type_name(sp.Dataset),
                )
                self.attach_mock(ds, mock)

            return sp.type_name(sp.Dataset), attach_info

        else:
            # By default, results of non external transforms (e.g. join,
            # sample) are Datasets and non external transforms are only applied
            # to Datasets
            mock_args = [self.mock(arg) for arg in arguments]
            named_mock_args = {
                name: self.mock(arg) for name, arg in named_arguments.items()
            }

            mock = transformed(
                transform,
                *mock_args,
                dataspec_type=sp.type_name(sp.Dataset),
                **named_mock_args,
            )

            def attach_info(ds: st.DataSpec) -> None:
                self.attach_mock(ds, mock)

            return sp.type_name(sp.Dataset), attach_info

    Edge = Tuple[st.DataSpec, st.DataSpec, st.Transform]

    def computation_graph(
        self, dataspec: st.DataSpec
    ) -> Dict[str, Union[st.DataSpec, st.Transform, st.Attribute, Edge]]:
        """Retreive all items necessary to compute a DataSpec.

        This function is used intensively to post DataSpecs, draw dot
        representationss, fetch statuses, and so on.
        """
        storage = self.storage()

        class ComputationGraphVisitor(st.Visitor):
            dataspecs: List[st.DataSpec] = list()
            transforms: Set[st.Transform] = set()
            edges: Set[Tuple(st.DataSpec, st.DataSpec, st.Transform)] = set()
            attributes: Set[st.Attribute] = set()
            graph: Dict[str, Set[str]] = dict()

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)
                    attributes = storage.referring(
                        visited, type_name=sp.type_name(sp.Attribute)
                    )
                    self.attributes.update([att for att in attributes])

                    if not visited.is_remote():
                        self.transforms.add(transform)
                        for argument in arguments:
                            argument.accept(self)
                            self.edges.add((argument, visited, transform))
                        for _, argument in named_arguments.items():
                            argument.accept(self)
                            self.edges.add((argument, visited, transform))

            def other(self, visited: st.DataSpec) -> None:
                if visited not in self.dataspecs:
                    self.dataspecs.append(visited)

        visitor = ComputationGraphVisitor()
        dataspec.accept(visitor)

        return {
            "dataspecs": visitor.dataspecs[::-1],
            "transforms": visitor.transforms,
            "attributes": visitor.attributes,
            "edges": visitor.edges,
        }

    def dot(
        self,
        dataspec: st.DataSpec,
        symbols: Dict[str, Optional[str]] = dict(),
        remote: bool = True,
    ) -> str:
        """GraphViz dot language representation of the graph.

        Statuses are represented with a color code. The symbols are the
        caller's symbol for the DataSpec wrapper
        (see DataSpecWrapper.dataspec_wrapper_symbols).
        """
        graph = self.computation_graph(dataspec)
        statuses = self._get_status(dataspec, remote=remote)

        edges, nodes, props = [], [], []
        for dataspec in graph["dataspecs"]:
            status = next(
                sta for sta in statuses if sta["id"] == dataspec.uuid()
            )
            nodes.append(self.node_repr(dataspec, status, symbols))
        for parent, child, transform in graph["edges"]:
            edges.append(
                f'"{parent.uuid()}" -> "{child.uuid()}"'
                f'[label="{transform.name()}"];'
            )
        props = [
            'node [style="rounded,filled"]',
        ]
        dot = ["digraph {"] + props + nodes + edges + ["}"]
        return "\n".join(dot)

    def node_repr(
        self,
        dataspec: st.DataSpec,
        status: Dict[str, Any],
        symbols: Dict[str, Optional[str]],
    ) -> str:
        """Style a graph node depending on its status and symbol."""
        shape = "box"
        FILLCOLORS = {
            "error": "#ff9c9c",
            "ready": "#9cffc5",
            "pending": "#ffc89c",
            "processing": "#9cbeff",
            "no_status": "#ffffff",
        }
        # Colors
        if status["status"] >= 400:
            fillcolor = FILLCOLORS["no_status"]
            color = FILLCOLORS["error"]
        else:
            fillcolor = FILLCOLORS[status["code"]]
            color = "black"

        # Labels
        if dataspec.prototype() == sp.Dataset:
            if dataspec.is_remote():
                label_type = "Source"
            elif dataspec.is_synthetic():
                label_type = "Synthetic data"
            else:
                label_type = "Transformed"
        else:
            label_type = "Scalar"
        label_type = label_type.replace('"', "'")

        symbol = symbols.get(dataspec.uuid())
        if symbol is None:
            symbol = "anonymous"

        msg = status["message"] if status["message"] else ""
        msg = msg.replace('"', "'")
        if msg:
            msg = "\n" + msg

        label = f"{label_type}: {symbol}{msg}"

        return (
            f'"{dataspec.uuid()}"[label="{label}", '
            f'fillcolor="{fillcolor}", color="{color}", shape={shape}]'
        )


def manager(
    storage: Storage, sdk_client: Client, **kwargs: str
) -> LocalSDKManager:
    properties = {"type": "local_sdk"}
    properties.update(kwargs)
    return LocalSDKManager(
        storage, sp.Manager(properties=properties), sdk_client=sdk_client
    )
