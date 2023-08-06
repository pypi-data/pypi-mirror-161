"""cosmian_secure_computation_client.log module."""

import logging

LOGGER = logging.getLogger("cscc")


def setup_logging(debug: bool = False):
    """Configure basic logging."""
    logging.basicConfig(format="[%(asctime)s] [%(name)36s] => %(message)s")
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
