"""Provide a client for the Open Exchange Rates API."""
from __future__ import annotations

from http import HTTPStatus
from types import TracebackType
from typing import Any

from aiohttp import ClientError, ClientResponse, ClientResponseError, ClientSession

from .exceptions import (
    OpenExchangeRatesAuthError,
    OpenExchangeRatesClientError,
    OpenExchangeRatesRateLimitError,
)
from .model import Latest

BASE_API_ENDPOINT = "https://openexchangerates.org/api/"


class Client:
    """Represent the client for the Open Exchange Rates API."""

    def __init__(self, api_key: str, session: ClientSession | None = None) -> None:
        """Initialize the client."""
        self.api_key = api_key
        self.session = session or ClientSession()

    async def request(self, endpoint: str, **kwargs: Any) -> ClientResponse:
        """Make a request."""
        url = f"{BASE_API_ENDPOINT}{endpoint}"
        try:
            return await self.session.get(url, raise_for_status=True, **kwargs)
        except ClientResponseError as err:
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise OpenExchangeRatesAuthError(err.message) from err
            if err.status == HTTPStatus.FORBIDDEN:
                raise OpenExchangeRatesAuthError(err.message) from err
            if err.status == HTTPStatus.TOO_MANY_REQUESTS:
                raise OpenExchangeRatesRateLimitError(err.message) from err
            raise OpenExchangeRatesClientError(err.message) from err
        except ClientError as err:
            raise OpenExchangeRatesClientError(f"Unknown error: {err}") from err

    async def get_latest(
        self, base: str = "USD", symbols: list[str] | None = None
    ) -> Latest:
        """Get the latest rates for the given base and symbols."""
        params = {"app_id": self.api_key, "base": base}
        if symbols:
            params["symbols"] = ",".join(symbols)
        response = await self.request("latest.json", params=params)
        return Latest(**(await response.json()))

    async def close(self) -> None:
        """Close the client."""
        await self.session.close()

    async def __aenter__(self) -> Client:
        """Enter the context manager."""
        return self

    async def __aexit__(
        self, exc_type: Exception, exc_value: str, traceback: TracebackType
    ) -> None:
        """Exit the context manager."""
        await self.close()
