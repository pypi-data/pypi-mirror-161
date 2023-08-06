"""cosmian_secure_computation_client.api.remote_attestation module."""

import base64
from typing import Optional, Dict, Any

import requests

from cryptography import x509
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat)
import jwt

from cosmian_secure_computation_client.util.base64 import (base64url_encode,
                                                           base64url_decode)


def microsoft_azure_attest(quote: str,
                           enclave_held_data: Optional[bytes]) -> Dict[str, Any]:
    """Attest request to Microsoft Azure Attestation (MAA) service.

    Parameters
    ----------
    quote : str
        Intel's quote encoded in base64.
    enclave_held_data : Optional[bytes]
        Data in the user report data section of the Intel's quote.

    Returns
    -------
    Dict[str, Any]
        JSON response of the MAA service API.

    """
    raw_quote: bytes = base64.b64decode(quote)
    payload: Dict[str, Any] = {"quote": base64url_encode(raw_quote)}

    if enclave_held_data is not None:
        payload["runtimeData"] = {
            "data": base64url_encode(enclave_held_data),
            "dataType": "Binary"
        }

    response = requests.post(
        url="https://sharedneu.neu.attest.azure.net/attest/SgxEnclave",
        params={
            "api-version": "2020-10-01"
        },
        json=payload
    )

    response.raise_for_status()

    return response.json()


def microsoft_signing_certs() -> Dict[str, Any]:
    """Retrieve Microsoft certificates to check Azure remote attestation."""
    response = requests.get(
        url="https://sharedneu.neu.attest.azure.net/certs",
    )

    return response.json()


def verify_jws(jws: str, jwks: Dict[str, Any]) -> Dict[str, Any]:
    """Check signature of the `jws` with keys in `jwks`.

    Parameters
    ----------
    jws : str
        JSON Web Token (JWT) which contains a JSON Web Signature (JWS).
    jwks : Dict[str, Any]
        JSON Web Key (JWK) set with public key.

    Returns
    -------
    Dict[str, Any]
        Decoded JWT if signature is verified.

    """
    header = jwt.get_unverified_header(jws)
    kid = header["kid"]

    for jwk in jwks["keys"]:
        if jwk["kid"] == kid:
            x5c, *_ = jwk["x5c"]
            assert jwk["kty"] == "RSA"
            raw_cert: bytes = base64url_decode(x5c)
            cert = x509.load_der_x509_certificate(raw_cert)
            return jwt.decode(
                jws,
                cert.public_key().public_bytes(
                    Encoding.PEM,
                    PublicFormat.PKCS1
                ).decode("utf-8"),
                algorithms=["RS256"]
            )

    raise Exception("can't verify MAA signature")


def azure_remote_attestation(quote: str,
                             enclave_held_data: Optional[bytes] = None
                             ) -> Dict[str, Any]:
    """Azure remote attestation with Microsoft Azure Attestation (MAA) service.

    Parameters
    ----------
    quote : str
        Intel's quote encoded in base64.
    enclave_held_data : Optional[bytes]
        Data in the user report data section of the Intel's quote.

    Returns
    -------
    Dict[str, Any]
        JSON response of the MAA service API.

    """
    token = microsoft_azure_attest(
        quote,
        enclave_held_data
    )["token"]
    certs: Dict[str, Any] = microsoft_signing_certs()

    return verify_jws(token, certs)
