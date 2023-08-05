"""Provide a base response model."""
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Represent a base response."""

    disclaimer: str
    license: str


class BaseRatesResponse(BaseResponse):
    """Represent a base rates response."""

    timestamp: int
    base: str
    rates: dict[str, float]
