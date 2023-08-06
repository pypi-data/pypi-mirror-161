"""cosmian_secure_computation_client.crypto.context module."""
import base64
import json
from pathlib import Path
from typing import Optional, List, Tuple, Union, Dict, Any, cast
from uuid import UUID

from cryptography.hazmat.primitives import serialization

from cosmian_secure_computation_client.crypto.helper import (ed25519_keygen,
                                                             ed25519_seed_keygen,
                                                             ed25519_to_x25519_pubkey,
                                                             encrypt,
                                                             decrypt,
                                                             derive_psk,
                                                             encrypt_file,
                                                             decrypt_file,
                                                             encrypt_directory,
                                                             decrypt_directory,
                                                             random_symkey,
                                                             pubkey_fingerprint,
                                                             seal,
                                                             sign)
from cosmian_secure_computation_client.side import Side
from cosmian_secure_computation_client.util.base64 import Base64Encoder
from cosmian_secure_computation_client.util.mnemonic import parse_words


class CryptoContext:
    """CryptoContext class for cryptographic keys.

    Parameters
    ----------
    computation_uuid : str
        Computation UUID (Universally Unique IDentifier) of the computation.
    side : Side
        Role in the computation. Could be Side.CodeProvider, Side.DataProvider or
        Side.ResultConsumer.
    words : Union[str, Tuple[str, str, str]]
        3 words used as the pre-shared secret between participants.
    ed25519_seed : Optional[bytes]
        Ed25519 private key used for signature.
    symkey :  Optional[bytes]
        XSalsa20-Poly1305 symmetric key used for encryption/decryption.

    Attributes
    ----------
    ed25519_pk : bytes
        Ed25519 public key.
    ed25519_seed : bytes
        Ed25519 seed.
    ed25519_sk : bytes
        Ed25519 private key.
    ed25519_fingerprint : bytes
        Fingerprint of the Ed25519 public key.
    _symkey : bytes
        Symmetric key used for encryption/decryption with XSalsa20-Poly1305.
    _words: Tuple[str, str, str]
        3 words used as the pre-shared secret between participants.
    preshared_sk : bytes
        Pre-shared key derived from the pre-shared secret.

    """

    def __init__(self,
                 computation_uuid: str,
                 side: Side,
                 words: Union[str, Tuple[str, str, str]],
                 ed25519_seed: Optional[bytes] = None,
                 symkey: Optional[bytes] = None) -> None:
        """Init constructor of CryptoContext."""
        self.computation_uuid: UUID = UUID(computation_uuid)
        self.side: Side = side
        self.ed25519_pk, self.ed25519_seed, self.ed25519_sk = (
            ed25519_keygen() if ed25519_seed is None else
            ed25519_seed_keygen(ed25519_seed)
        )  # type: bytes, bytes, bytes
        self.ed25519_fingerprint: bytes = pubkey_fingerprint(self.ed25519_pk)
        self._symkey: bytes = symkey if symkey else random_symkey()
        self._words: Tuple[str, str, str] = (parse_words(words)
                                             if isinstance(words, str) else words)
        self.preshared_sk: bytes = derive_psk(self._words)

    @classmethod
    def from_path(cls,
                  computation_uuid: str,
                  side: Side,
                  words: Union[str, Tuple[str, str, str]],
                  private_key: Optional[Path],
                  password: Optional[bytes],
                  symmetric_key: Optional[Path]):
        """Create `CryptoContext` from files.

        Parameters
        ----------
        computation_uuid : str
            Computation UUID (Universally Unique IDentifier) of the computation.
        side : Side
            Role in the computation. Could be Side.CodeProvider, Side.DataProvider or
            Side.ResultConsumer.
        words : Union[str, Tuple[str, str, str]]
            3 words used as the pre-shared secret between participants.
        private_key : Optional[Path]
            Ed25519 private key file in PEM format for digital signature.
        password :  Optional[bytes]
            Password for PEM private key file.
        symmetric_key :  Optional[Path]
            XSalsa20-Poly1305 symmetric key used for encryption/decryption stored as
            raw bytes in a file.

        """
        ed25519_seed: Optional[bytes] = None
        symkey: Optional[bytes] = None

        if private_key:
            if not private_key.exists():
                raise Exception(f"can't find private key file: {private_key}")

            ed25519_seed = serialization.load_pem_private_key(
                data=private_key.read_bytes(),
                password=password
            ).private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )

        if symmetric_key:
            if not symmetric_key.exists():
                raise Exception(f"can't find symmetric key file: {symmetric_key}")

            symkey = symmetric_key.read_bytes()

        return cls(computation_uuid, side, words, ed25519_seed, symkey)

    @classmethod
    def from_dict(cls, d: Dict[str, Union[str, bytes]]):
        """Create `CryptoContext` from dict."""
        return cls(
            computation_uuid=cast(str, d["computation_uuid"]),
            side=Side[cast(str, d["side"])],
            words=cast(str, d["words"]),
            ed25519_seed=cast(bytes, d["ed25519_seed"]),
            symkey=cast(bytes, d["symkey"])
        )

    @classmethod
    def from_json(cls, value: str):
        """Create `CryptoContext` from JSON string."""
        d: Dict[str, Any] = json.loads(value)

        d["ed25519_seed"] = base64.b64decode(d["ed25519_seed"])
        d["symkey"] = base64.b64decode(d["symkey"])

        return cls.from_dict(d)

    def to_dict(self) -> Dict[str, Union[str, bytes]]:
        """Serialize to dict."""
        return {
            "computation_uuid": str(self.computation_uuid),
            "side": str(self.side),
            "words": "-".join(self.words),
            "symkey": self._symkey,
            "ed25519_seed": self.ed25519_seed
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=Base64Encoder)

    @property
    def public_key(self) -> bytes:
        """Ed25519 public key."""
        return self.ed25519_pk

    @property
    def fingerprint(self) -> bytes:
        """Fingerprint of the public key."""
        return self.ed25519_fingerprint

    @property
    def symkey(self) -> bytes:
        """XSalsa20-Poly1305 symmetric key used for encryption."""
        return self._symkey

    @property
    def words(self) -> Tuple[str, str, str]:
        """Pre-shared secret between participants."""
        return self._words

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt bytes `data` using XSalsa20-Poly1305.

        Parameters
        ----------
        data : bytes
            Data to be encrypted.

        Returns
        -------
        bytes
            Ciphertext of `data` encrypted using `self._symkey`.

        """
        return encrypt(data, self._symkey)

    def encrypt_file(self, path: Path) -> Path:
        """Encrypt file `path` using XSalsa20-Poly1305.

        Parameters
        ----------
        path : Path
            Path to the data to be encrypted.

        Returns
        -------
        Path
            Path to the encrypted file `path` with `self._symkey`.

        """
        return encrypt_file(path, self._symkey)

    def encrypt_directory(self,
                          dir_path: Path,
                          patterns: List[str],
                          exceptions: List[str],
                          dir_exceptions: List[str],
                          out_dir_path: Path) -> bool:
        """Encrypt the content of directory `dir_path` using XSalsa20-Poly1305.

        Parameters
        ----------
        dir_path : Path
            Path to the directory to be encrypted.
        patterns: List[str]
            List of patterns to be matched in the directory.
        exceptions: List[str]
            List of files which won't be encrypted.
        dir_exceptions: List[str]
            List of directories which won't be encrypted recursively.
        out_dir_path: Path
            Output directory path.

        Returns
        -------
        bool
            True if success, raise an exception otherwise.

        """
        return encrypt_directory(dir_path,
                                 patterns,
                                 self._symkey,
                                 exceptions,
                                 dir_exceptions,
                                 out_dir_path)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes `encrypted_data` using XSalsa20-Poly1305.

        Parameters
        ----------
        encrypted_data : bytes
            Encrypted data to be decrypted.

        Returns
        -------
        bytes
            Cleartext of `encrypted_data` decrypted using `self._symkey`.

        """
        return decrypt(encrypted_data, self._symkey)

    def decrypt_file(self, path: Path) -> Path:
        """Decrypt file `path` using XSalsa20-Poly1305.

        Parameters
        ----------
        path : Path
            Path to the data to be decrypted.

        Returns
        -------
        Path
            Path to the decrypted file `path` with `self._symkey`.

        """
        return decrypt_file(path, self._symkey)

    def decrypt_directory(self, dir_path: Path) -> bool:
        """Decrypt the content of directory `dir_path` using XSalsa20-Poly1305.

        Parameters
        ----------
        dir_path : Path
            Path to the directory to be decrypted.

        Returns
        -------
        bool
            True if success, raise an exception otherwise.

        Notes
        -----
        It looks for files with extension ENC_EXT.

        """
        return decrypt_directory(dir_path, self._symkey)

    def sign(self, data: bytes) -> bytes:
        """Sign `data` with `self.ed25519_seed`.

        Parameters
        ----------
        data : bytes
            Data to be signed.

        Returns
        -------
        bytes
            64 bytes Ed25519 signature.

        """
        return sign(data, self.ed25519_seed)

    def seal_symkey(self, ed25519_recipient_pk: bytes) -> bytes:
        """Seal your symmetric key and sign the box.

        Parameters
        ----------
        ed25519_recipient_pk : bytes
            Recipent X25519 public key (32 bytes).

        Returns
        -------
        bytes
            sig (64) || seal_box (112).


        Notes
        -----
        Use seal box of libsodium (X25519 and XSalsa20-Poly1305) by converting the
        Ed25519 public key into X25519 public key first::

            ephemeral_pk ‖ box(m,
                               recipient_pk,
                               ephemeral_sk,
                               nonce=blake2b(ephemeral_pk ‖ x25519_recipient_pk)))

        """
        x25519_recipient_pk: bytes = ed25519_to_x25519_pubkey(ed25519_recipient_pk)
        # seal_box = SealBox(self.preshared_sk || self._symkey,
        #                    x25519_recipient_pk) (112)
        seal_box: bytes = seal(self.preshared_sk + self._symkey, x25519_recipient_pk)
        # sig = Sign(computation_uuid || seal_box, self.ed25519_seed) (64)
        sig: bytes = self.sign(self.computation_uuid.bytes + seal_box)

        return sig + seal_box
