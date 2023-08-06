"""cosmian_secure_computation_client.participant.result_consumer module."""

import time
from typing import Optional, cast

import requests

from cosmian_secure_computation_client.api.provider import download_result
from cosmian_secure_computation_client.participant.base import BaseAPI
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.crypto.context import CryptoContext


class ResultConsumerAPI(BaseAPI):
    """ResultConsumerAPI class derived from BaseAPI.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    """

    def __init__(self, token: str, ctx: CryptoContext) -> None:
        """Init constructor of ResultConsumerAPI."""
        super().__init__(Side.ResultConsumer, token, ctx)

    def fetch_result(self, computation_uuid: str) -> Optional[bytes]:
        """Download the result of the computation if available."""
        self.log.debug("Result available")
        r: requests.Response = download_result(
            conn=self.conn,
            computation_uuid=computation_uuid
        )

        if r.status_code == requests.codes["accepted"]:
            return None

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        encrypted_result: bytes
        try:
            # backward compatibility with old API
            encrypted_result = bytes.fromhex(r.json()["message"])
        except requests.JSONDecodeError:
            encrypted_result = r.content

        self.log.debug("Decrypt result...")
        result: bytes = self.ctx.decrypt(encrypted_result)
        self.log.info("Result received and successfully decrypted")

        return result

    def wait_result(self,
                    computation_uuid: str,
                    sleep_duration: int = 30) -> bytes:
        """Wait for the result to be available and fetch it."""
        self.log.info("Waiting for result...")
        while True:
            comp = self.get_computation(computation_uuid)

            if comp.runs.current is None and len(comp.runs.previous) == 1:
                run = comp.runs.previous[0]
                if run.exit_code != 0:
                    raise Exception("Execution failed: "
                                    f"{(run.exit_code, run.stdout, run.stderr)}")
                return cast(bytes, self.fetch_result(computation_uuid))

            time.sleep(sleep_duration)
