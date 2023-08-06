"""cosmian_secure_computation_client.participant.common module."""

import logging
import os
import time
from pathlib import Path
from typing import List

import requests
from cosmian_secure_computation_client.api.auth import Connection
from cosmian_secure_computation_client.api.provider import (computation,
                                                            computations,
                                                            download_code,
                                                            key_provisioning,
                                                            register)
from cosmian_secure_computation_client.computations import (Computation,
                                                            EnclaveIdentity)
from cosmian_secure_computation_client.crypto.context import CryptoContext
from cosmian_secure_computation_client.log import LOGGER
from cosmian_secure_computation_client.side import Side


class BaseAPI:
    """BaseAPI class shared to all APIs.

    Parameters
    ----------
    side : Side
        Either Side.CodeProvider, Side.DataProvider or Side.ResultConsumer.
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    Attributes
    ----------
    side : Side
        Either Side.CodeProvider, Side.DataProvider or Side.ResultConsumer.
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.
    conn : Connection
        Manage authentication to Cosmian's backend.

    """

    def __init__(self, side: Side, token: str, ctx: CryptoContext) -> None:
        """Init constructor of BaseAPI."""
        self.side: Side = side
        self.ctx: CryptoContext = ctx
        self.conn = Connection(base_url=os.getenv(
            'COSMIAN_BASE_URL', default="https://backend.cosmian.com"),
                               refresh_token=token)
        self.log = logging.getLogger(
            f"cscc.{side}.{self.ctx.fingerprint.hex()}")
        self.log.setLevel(LOGGER.level)

    def register(self, computation_uuid: str) -> Computation:
        """Send your public key and role for a specific `computation_uuid`."""
        r: requests.Response = register(conn=self.conn,
                                        computation_uuid=computation_uuid,
                                        side=self.side,
                                        public_key=self.ctx.public_key)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        self.log.info("Participant %s registered to the enclave",
                      self.ctx.public_key.hex()[:16])

        return Computation.from_json_dict(r.json())

    def get_computation(self, computation_uuid: str) -> Computation:
        """Retrieve computation information related to `computation_uuid`."""
        r: requests.Response = computation(conn=self.conn,
                                           computation_uuid=computation_uuid)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())

    def get_computations(self) -> List[Computation]:
        """Retriveve all computations related to your account."""
        r: requests.Response = computations(conn=self.conn)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        cs: List[Computation] = [
            Computation.from_json_dict(dct) for dct in r.json()
        ]
        LOGGER.info("Computations available: %s",
                    [(c.name, c.uuid) for c in cs])

        return cs

    def key_provisioning(self, computation_uuid: str,
                         enclave_public_key: bytes) -> Computation:
        """Send your symmetric key sealed for `enclave_public_key`."""
        self.log.debug("Sealing symmetric key for %s and signing...",
                       enclave_public_key.hex()[:16])
        sealed_symmetric_key: bytes = self.ctx.seal_symkey(
            ed25519_recipient_pk=enclave_public_key)

        r: requests.Response = key_provisioning(
            conn=self.conn,
            computation_uuid=computation_uuid,
            side=self.side,
            sealed_symmetric_key=sealed_symmetric_key)
        self.log.info("Key provisionning done")

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())

    def wait_for_enclave_identity(self,
                                  computation_uuid: str,
                                  sleep_duration: int = 10) -> bytes:
        """Wait for enclave's public key to be available."""
        comp = self.get_computation(computation_uuid)

        self.log.info("Waiting for enclave's identity...")
        while comp.enclave.identity is None:
            time.sleep(float(sleep_duration))
            comp = self.get_computation(computation_uuid)

        enclave_public_key: bytes
        if isinstance(comp.enclave.identity, EnclaveIdentity):
            enclave_public_key = comp.enclave.identity.public_key
        else:
            raise Exception(f"Failed to lock enclave: {comp.enclave.identity}")

        self.log.info("Enclave's identity generated: %s",
                      enclave_public_key.hex()[:16])

        return enclave_public_key

    def download_code(
        self,
        computation_uuid: str,
        directory_path: Path,
    ) -> Path:
        """Send back your Python code encrypted on a specific `computation_uuid`."""
        tar_path = directory_path / f"{computation_uuid}_code.tar"
        self.log.debug("Tar encrypted code in '%s'", tar_path.name)

        r: requests.Response = download_code(
            conn=self.conn,
            computation_uuid=computation_uuid,
        )

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        tar_path.write_bytes(r.content)

        return tar_path
