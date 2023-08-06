from dataclasses import dataclass
from typing import Any, Optional

from conduit_sdk.common.schema import DataColumnSchema


@dataclass
class ResponseSchema:
    config: dict[str, Any]
    columns: list[DataColumnSchema]
    vault: Optional[str] = None


@dataclass
class RequestSchema:
    config: dict[str, Any]
    columns: list[DataColumnSchema]
    date_from: str  # format `DATE_FORMAT`
    date_to: str  # format `DATE_FORMAT`
    secrets: Optional[dict[str, Any]]


@dataclass
class QueryParams:
    origin: str
    vault_token: Optional[str] = None
    vault_url: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
