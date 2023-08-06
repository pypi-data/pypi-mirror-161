"""cosmian_secure_computation_client.api.provider module."""

from pathlib import Path
from typing import List

import requests

from cosmian_secure_computation_client.api.auth import Connection
from cosmian_secure_computation_client.side import Side


def create_computation(conn: Connection,
                       name: str,
                       cp_mail: str,
                       dps_mail: List[str],
                       rcs_mail: List[str],
                       dev_mode: bool) -> requests.Response:
    """POST `/computations` (for CO only)."""
    return conn.post(
        url="/computations",
        json={
            "name": name,
            "code_provider_email": cp_mail,
            "data_providers_emails": dps_mail,
            "result_consumers_emails": rcs_mail,
            "dev_mode": dev_mode
        }
    )


def computations(conn: Connection) -> requests.Response:
    """GET `/computations` (for CO, CP, DP and RC)."""
    return conn.get(url="/computations")


def computation(conn: Connection,
                computation_uuid: str) -> requests.Response:
    """GET `/computations/{computation_uuid}` (for CP, DP and RC)."""
    return conn.get(url=f"/computations/{computation_uuid}")


def register(conn: Connection,
             computation_uuid: str,
             side: Side,
             public_key: bytes) -> requests.Response:
    """POST `/computations/{computation_uuid}/register` (for CP, DP and RC)."""
    return conn.post(
        url=f"/computations/{computation_uuid}/register",
        json={
            "public_key": public_key.hex(),
            "side": str(side),
        }
    )


def upload_code(conn: Connection,
                computation_uuid: str,
                tar_path: Path,
                keep: bool = True) -> requests.Response:
    """POST `/computations/{computation_uuid}/code` (for CP only)."""
    if not tar_path.exists():
        raise FileNotFoundError("Can't find tar file!")

    with tar_path.open("rb") as fp:
        response: requests.Response = conn.post(
            url=f"/computations/{computation_uuid}/code",
            files={
                "file": (tar_path.name,
                         fp,
                         "application/tar",
                         {"Expires": "0"})
            },
            timeout=None
        )

    if not keep:
        tar_path.unlink()

    return response


def upload_data(conn: Connection,
                computation_uuid: str,
                name: str,
                data: bytes) -> requests.Response:
    """POST `/computations/{computation_uuid}/data` (for DP only)."""
    return conn.post(
        url=f"/computations/{computation_uuid}/data",
        files={
            "file": (f"{name}", data, "application/octet-stream", {"Expires": "0"})
        },
        timeout=None
    )


def done(conn: Connection,
         computation_uuid: str) -> requests.Response:
    """POST `/computations/{computation_uuid}/data/done` (for DP only)."""
    return conn.post(url=f"/computations/{computation_uuid}/data/done")


def key_provisioning(conn: Connection,
                     computation_uuid: str,
                     side: Side,
                     sealed_symmetric_key: bytes) -> requests.Response:
    """POST `/computations/{computation_uuid}/key/provisioning` (for CP, DP and RC)."""
    return conn.post(
        url=f"/computations/{computation_uuid}/key/provisioning",
        json={
            "role": str(side),
            "sealed_symmetric_key": list(sealed_symmetric_key)
        }
    )


def download_result(conn: Connection,
                    computation_uuid: str) -> requests.Response:
    """GET `/computations/{computation_uuid}/results` (for RC only)."""
    return conn.get(url=f"/computations/{computation_uuid}/results")


def download_code(conn: Connection,
                  computation_uuid: str) -> requests.Response:
    """GET `/computations/{computation_uuid}/code`."""
    return conn.get(url=f"/computations/{computation_uuid}/code")


def reset_code(conn: Connection,
               computation_uuid: str) -> requests.Response:
    """DELETE `/computations/{computation_uuid}/code` (for CP only)."""
    return conn.delete(url=f"/computations/{computation_uuid}/code")


def reset_data(conn: Connection,
               computation_uuid: str) -> requests.Response:
    """DELETE `/computations/{computation_uuid}/data` (for DP only)."""
    return conn.delete(url=f"/computations/{computation_uuid}/code")
