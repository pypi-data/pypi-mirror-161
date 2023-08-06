"""cosmian_secure_computation_client.side module."""

from enum import Enum


class Side(Enum):
    """Side class for participant roles."""

    CodeProvider = 0
    DataProvider = 1
    ResultConsumer = 2

    def __str__(self) -> str:
        """Use name for string representation."""
        return f"{self.name}"

    def __bytes__(self) -> bytes:
        """Bytes representation."""
        return bytes(self.value)
