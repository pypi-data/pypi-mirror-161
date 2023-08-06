"""cosmian_secure_computation_client.computations module."""

from dataclasses import dataclass
from typing import Optional, Dict, Union, List
from enum import Enum

import inspect


class Role(Enum):
    """Subdict in Computation.my_roles."""

    ComputationOwner = "ComputationOwner"
    CodeProvider = "CodeProvider"
    DataProvider = "DataProvider"
    ResultConsumer = "ResultConsumer"

    def __str__(self) -> str:
        """Use name for string representation."""
        return f"{self.name}"


@dataclass(frozen=True)
class PublicKey:
    """Subdict in Computation.enclave.identity.public_key."""

    fingerprint: bytes
    content: str
    uploaded_at: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(PublicKey, json)


@dataclass(frozen=True)
class Owner:
    """Subdict in Computation.owner."""

    uuid: str
    email: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(Owner, json)


@dataclass(frozen=True)
class CodeProvider:
    """Subdict in Computation.code_provider."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    code_uploaded_at: Optional[str]
    symmetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None
                              if json['public_key'] is None
                              else PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(CodeProvider, json)


@dataclass(frozen=True)
class DataProvider:
    """Subdict in Computation.data_providers."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    starting_uploading_at: Optional[str]
    done_uploading_at: Optional[str]
    symmetric_key_uploaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None
                              if json['public_key'] is None
                              else PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(DataProvider, json)


@dataclass(frozen=True)
class ResultConsumer:
    """Subdict in Computation.result_consumers."""

    uuid: str
    email: str
    public_key: Optional[PublicKey]
    symmetric_key_uploaded_at: Optional[str]
    result_downloaded_at: Optional[str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = (None
                              if json['public_key'] is None
                              else PublicKey.from_json_dict(json['public_key']))

        return construct_dataclass(ResultConsumer, json)


@dataclass(frozen=True)
class EnclaveIdentity:
    """Subdict in Computation.enclave.identity."""

    status: str
    public_key: bytes
    # Some endpoints omit the manifest in the response for performance reasons,
    # please call `get_computation()` to fetch it
    manifest: Optional[str]
    quote: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['public_key'] = bytes(json['public_key'])

        return construct_dataclass(EnclaveIdentity, json)


@dataclass(frozen=True)
class EnclaveIdentityLockError:
    """Subdict in Computation.enclave.identity."""

    status: str
    stdout: str
    stderr: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(EnclaveIdentityLockError, json)


@dataclass(frozen=True)
class Enclave:
    """Subdict in Computation.enclave."""

    identity: Optional[Union[EnclaveIdentity, EnclaveIdentityLockError]]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        if json['identity'] is not None:
            if json['identity']['status'] == "Locked":
                json['identity'] = EnclaveIdentity.from_json_dict(json['identity'])
            elif json['identity']['status'] == "Failed":
                json['identity'] = EnclaveIdentityLockError.from_json_dict(
                    json['identity']
                )
            else:
                raise ValueError(
                    f"Invalid status {json['identity']['status']} for enclave identity "
                    "('Locked' or 'Failed' expected). Maybe update your client?"
                )

        return construct_dataclass(Enclave, json)


@dataclass(frozen=True)
class CurrentRun:
    """Subdict in Comutation.runs.current."""

    created_at: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(CurrentRun, json)


@dataclass(frozen=True)
class PreviousRun:
    """Subdict in Computation.runs.previous."""

    created_at: str
    ended_at: str
    exit_code: int
    stdout: str
    stderr: str
    results_fetches_datetimes_by_result_consumers_uuid: Dict[str, str]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        return construct_dataclass(PreviousRun, json)


@dataclass(frozen=True)
class Runs:
    """Subdict in Computation.runs."""

    current: Optional[CurrentRun]
    previous: List[PreviousRun]

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['current'] = (None
                           if json['current'] is None
                           else CurrentRun.from_json_dict(json['current']))
        json['previous'] = list(map(PreviousRun.from_json_dict, json['previous']))

        return construct_dataclass(Runs, json)


@dataclass(frozen=True)
class Computation:
    """Computation dataclass representing JSON response."""

    uuid: str
    name: str
    owner: Owner
    code_provider: CodeProvider
    data_providers: List[DataProvider]
    result_consumers: List[ResultConsumer]
    enclave: Enclave
    runs: Runs
    my_roles: List[Role]
    created_at: str

    @staticmethod
    def from_json_dict(json):
        """Construct dataclass from dict."""
        json['owner'] = Owner.from_json_dict(json['owner'])
        json['code_provider'] = CodeProvider.from_json_dict(json['code_provider'])
        json['data_providers'] = list(map(DataProvider.from_json_dict,
                                          json['data_providers']))
        json['result_consumers'] = list(map(ResultConsumer.from_json_dict,
                                            json['result_consumers']))
        json['enclave'] = Enclave.from_json_dict(json['enclave'])
        json['runs'] = Runs.from_json_dict(json['runs'])
        json['my_roles'] = list(map(Role, json['my_roles']))

        return construct_dataclass(Computation, json)


def construct_dataclass(dc, json):
    """Dataclass builder."""
    sig = inspect.signature(dc)
    filter_keys = [param.name for param in sig.parameters.values() if
                   param.kind == param.POSITIONAL_OR_KEYWORD]
    filtered_dict = {filter_key: json.get(filter_key, None) for filter_key in filter_keys}
    return dc(**filtered_dict)
