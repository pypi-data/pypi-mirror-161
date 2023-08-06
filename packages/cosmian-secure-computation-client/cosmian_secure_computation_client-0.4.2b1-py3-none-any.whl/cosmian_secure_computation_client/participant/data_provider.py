"""cosmian_secure_computation_client.participant.data_provider module."""

from pathlib import Path
from typing import Iterable

import requests

from cosmian_secure_computation_client.api.provider import upload_data, reset_data, done
from cosmian_secure_computation_client.participant.base import BaseAPI
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.crypto.context import CryptoContext
from cosmian_secure_computation_client.computations import Computation


class DataProviderAPI(BaseAPI):
    """DataProviderAPI class derived from BaseAPI.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    """

    def __init__(self, token: str, ctx: CryptoContext) -> None:
        """Init constructor of DataProviderAPI."""
        super().__init__(Side.DataProvider, token, ctx)

    def upload_data(self,
                    computation_uuid: str,
                    data_name: str,
                    data: bytes) -> None:
        """Upload encrypted data on `computation_uuid`."""
        encrypted_data_name: str = f"{data_name}.enc"
        self.log.debug("Encrypting data '%s' to '%s'...", data_name, encrypted_data_name)
        r: requests.Response = upload_data(
            conn=self.conn,
            computation_uuid=computation_uuid,
            name=encrypted_data_name,
            data=self.ctx.encrypt(data)
        )
        self.log.info("Encrypted data '%s' sent", encrypted_data_name)

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    def upload_files(self, computation_uuid: str, paths: Iterable[Path]) -> None:
        """Upload encrypted files on `computation_uuid`."""
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError

            self.upload_data(computation_uuid, path.name, path.read_bytes())

    def done(self, computation_uuid: str) -> Computation:
        """Confirm that all data has been sent."""
        r: requests.Response = done(
            conn=self.conn,
            computation_uuid=computation_uuid
        )

        self.log.info("Sending data done")

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())

    def reset(self, computation_uuid: str) -> Computation:
        """Remove all data sent for a specific `computation_uuid`."""
        self.log.info("Reset data sent")
        r: requests.Response = reset_data(
            conn=self.conn,
            computation_uuid=computation_uuid
        )

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())
