"""cosmian_secure_computation_client.participant.computation_owner module."""

from typing import List, Tuple
import os

import requests

from cosmian_secure_computation_client.api.provider import (create_computation,
                                                            computations)
from cosmian_secure_computation_client.api.auth import Connection
from cosmian_secure_computation_client.computations import Computation
from cosmian_secure_computation_client.log import LOGGER
from cosmian_secure_computation_client.util.mnemonic import random_words


class ComputationOwnerAPI:
    """ComputationOwnerAPI class.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.

    Attributes
    ----------
    conn : Connection
        Manage authentication to Cosmian's backend.

    """

    def __init__(self, token: str) -> None:
        """Init constructor of ComputationOwnerAPI."""
        self.conn = Connection(
            base_url=os.getenv("COSMIAN_BASE_URL",
                               default="https://backend.cosmian.com"),
            refresh_token=token
        )

    @staticmethod
    def random_words() -> Tuple[str, str, str]:
        """Generate 3 random words to be used as pre-shared secret."""
        w1, w2, w3 = random_words()  # type: str, str, str
        LOGGER.info("Generating pre-shared secret: '%s %s %s'", w1, w2, w3)

        return w1, w2, w3

    def create_computation(self,
                           name: str,
                           code_provider_email: str,
                           data_providers_emails: List[str],
                           result_consumers_emails: List[str],
                           dev_mode: bool = False) -> Computation:
        """Invite participants to a new computation named `name`."""
        r: requests.Response = create_computation(
            conn=self.conn,
            name=name,
            cp_mail=code_provider_email,
            dps_mail=data_providers_emails,
            rcs_mail=result_consumers_emails,
            dev_mode=dev_mode
        )

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        c: Computation = Computation.from_json_dict(r.json())
        LOGGER.info("Computation '%s' created: %s", c.name, c.uuid)

        return c

    def get_computations(self) -> List[Computation]:
        """Retriveve all computations related to your account."""
        r: requests.Response = computations(conn=self.conn)

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        cs: List[Computation] = [Computation.from_json_dict(dct) for dct in r.json()]
        LOGGER.info("Computations available: %s", [(c.name, c.uuid) for c in cs])

        return cs
