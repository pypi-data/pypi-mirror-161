import io
import pickle as pkl
from http import HTTPStatus
from itertools import count
from time import sleep
from typing import List

import pyarrow as pa
import pyarrow.parquet as pq
import requests
import sarus_data_spec.typing as st
from sarus_data_spec.protobuf.utilities import dict_serialize

from sarus.typing import Client


def fetch_synthetic(client: Client, id: str) -> pa.Table:
    """Fetch synthetic data for a Dataset."""
    resp = client.session.get(
        f"{client.base_url}/synthetic_data/{id}",
        stream=True,
        params={
            "textual_categories": True,
            "rows_number": None,
        },
    )
    if resp.status_code > 200:
        raise Exception(
            f"Error while retrieving synthetic data. "
            f"Gateway answer was: \n{resp}"
        )

    synthetic_table = pq.ParquetFile(io.BytesIO(resp.content)).read()

    return synthetic_table


def post_graph(
    client: Client,
    target: st.DataSpec,
    dataspecs: List[st.DataSpec],
    transforms: List[st.Transform],
    attributes,
    execute: bool,
) -> requests.Response:
    """Post a DataSpec and all its ancestors and attributes."""
    # TODO Ask server what it already has
    payload = pkl.dumps(
        {
            "items": [
                {
                    "target": target.uuid(),
                    "dataspecs": [
                        dict_serialize(dataspec.protobuf())
                        for dataspec in dataspecs
                    ],
                    "transforms": [
                        dict_serialize(transform.protobuf())
                        for transform in transforms
                    ],
                    "attributes": [
                        dict_serialize(attribute.protobuf())
                        for attribute in attributes
                    ],
                }
            ]
        }
    )

    resp = client.session.post(
        url=f"{client.base_url}/v2/dataspecs",
        data=payload,
        params={"execute": "true" if execute else "false"},
    )

    return resp


def get_dataspec_status(
    client: Client,
    dataspecs: List[st.DataSpec],
) -> requests.Response:
    """Fetch information on a DataSpec status on the server."""
    return client.session.get(
        url=f"{client.base_url}/v2/dataspecs/status",
        params={"uuids": [ds.uuid() for ds in dataspecs]},
    )


def get_dataspec(
    client: Client,
    dataspec: st.DataSpec,
    max_attempts: int = 10,
    interval: int = 4,
) -> bytes:
    """Fetch a DataSpec value from the server."""
    resp = client.session.get(
        url=f"{client.base_url}/v2/dataspecs", params={"uuid": dataspec.uuid()}
    )
    if resp.status_code >= HTTPStatus.BAD_REQUEST:
        msg = resp.json()["message"]
        raise ValueError(f"Server - {msg}")

    attempts = count()
    while (
        resp.status_code == HTTPStatus.ACCEPTED
        and next(attempts) <= max_attempts
    ):
        sleep(interval)
        resp = client.session.get(
            url=f"{client.base_url}/v2/dataspecs",
            params={"uuid": dataspec.uuid()},
        )
        if resp.status_code >= HTTPStatus.BAD_REQUEST:
            msg = resp.json()["message"]
            raise ValueError(f"Server - {msg}")

    if resp.status_code != HTTPStatus.OK:
        msg = resp.json()["message"]
        raise ValueError(f"Server - {msg}")
    for data in resp.iter_content(chunk_size=1 << 10):
        yield data


def delete_dataspec(client: Client, uuid: str) -> requests.Response:
    """Delete a DataSpec from the server."""
    return client.session.delete(
        url=f"{client.base_url}/v2/dataspecs",
        params={"uuid": uuid},
    )
