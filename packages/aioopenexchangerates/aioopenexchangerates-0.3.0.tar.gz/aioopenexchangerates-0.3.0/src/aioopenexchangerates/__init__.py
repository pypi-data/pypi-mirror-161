"""Fetch rates from openexchangerates with aiohttp."""
from .client import Client
from .exceptions import (
    OpenExchangeRatesAuthError,
    OpenExchangeRatesClientError,
    OpenExchangeRatesError,
)
from .model import Latest

__all__ = [
    "OpenExchangeRatesError",
    "OpenExchangeRatesAuthError",
    "OpenExchangeRatesClientError",
    "Client",
    "Latest",
]
__version__ = "0.3.0"
