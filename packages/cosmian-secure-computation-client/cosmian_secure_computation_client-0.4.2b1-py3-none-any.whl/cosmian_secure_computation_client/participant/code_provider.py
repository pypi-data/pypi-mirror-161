"""cosmian_secure_computation_client.participant.code_provider module."""

from pathlib import Path
import tempfile
from typing import Dict, List, Optional

import requests

from cosmian_secure_computation_client.api.provider import upload_code, reset_code
from cosmian_secure_computation_client.util.fs import tar
from cosmian_secure_computation_client.participant.base import BaseAPI
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.crypto.context import CryptoContext
from cosmian_secure_computation_client.computations import Computation


class CodeProviderAPI(BaseAPI):
    """CodeProviderAPI class derived from BaseAPI.

    Parameters
    ----------
    token : str
        Refresh token to authenticate with Cosmian's backend.
    ctx : CryptoContext
        Context with cryptographic secrets.

    """

    def __init__(self, token: str, ctx: CryptoContext) -> None:
        """Init constructor of CodeProviderAPI."""
        super().__init__(Side.CodeProvider, token, ctx)

    def upload_code(self,
                    computation_uuid: str,
                    directory_path: Path,
                    patterns: Optional[List[str]] = None,
                    file_exceptions: Optional[List[str]] = None,
                    dir_exceptions: Optional[List[str]] = None
                    ) -> Dict[str, str]:
        """Send your Python code encrypted on a specific `computation_uuid`."""
        if not (directory_path / "run.py").exists():
            raise FileNotFoundError("Entrypoint 'run.py' not found!")

        enc_directory_path: Path = (Path(tempfile.gettempdir()) /
                                    "cscc" /
                                    f"{computation_uuid}" /
                                    directory_path.name)

        self.log.debug("Encrypt code in %s to %s...",
                       directory_path,
                       enc_directory_path)
        self.ctx.encrypt_directory(
            dir_path=directory_path,
            patterns=(["*"]
                      if patterns is None
                      else patterns),
            exceptions=(["run.py"]
                        if file_exceptions is None
                        else file_exceptions + ["run.py"]),
            dir_exceptions=([]
                            if dir_exceptions is None
                            else dir_exceptions),
            out_dir_path=enc_directory_path
        )
        tar_path = tar(
            dir_path=enc_directory_path,
            tar_path=enc_directory_path / f"{enc_directory_path.name}.tar"
        )
        self.log.debug("Tar encrypted code in '%s'", tar_path.name)

        r: requests.Response = upload_code(
            conn=self.conn,
            computation_uuid=computation_uuid,
            tar_path=tar_path
        )

        self.log.info("Encrypted code '%s' sent", tar_path.name)

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return r.json()

    def reset(self, computation_uuid: str) -> Computation:
        """Delete the Python code of `computation_uuid` on Cosmian's backend."""
        self.log.info("Reset code sent")
        r: requests.Response = reset_code(
            conn=self.conn,
            computation_uuid=computation_uuid
        )

        if not r.ok:
            raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

        return Computation.from_json_dict(r.json())
