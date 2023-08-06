import json
from json import JSONDecodeError
from typing import Any, Mapping, Optional, cast
from urllib.parse import urlparse

from conduit_sdk.common.schema import AggregationType, ColumnKind, ColumnType, DataColumnSchema
from conduit_sdk.errors import ValidationError

from .schema import QueryParams, RequestSchema


def parse_query_params(
    query_params: Mapping[str, Any],
    vault_required: bool = True,
) -> QueryParams:
    origin = cast(str, _get_query_param(query_params, 'origin'))
    vault_token = _get_query_param(query_params, 'vault_token', vault_required)
    vault_url = _get_query_param(query_params, 'vault_url', vault_required)
    payload = _get_payload(query_params)

    _validate_origin(origin)

    return QueryParams(
        origin=origin,
        vault_token=vault_token,
        vault_url=vault_url,
        payload=payload,
    )


def parse_request_schema(body: dict[str, Any]) -> RequestSchema:
    config = _get_body_field(body, 'config')
    columns = _parse_columns(_get_body_field(body, 'columns'))
    date_from = _get_body_field(body, 'date_from')
    date_to = _get_body_field(body, 'date_to')
    secrets = _get_body_field(body, 'secrets')

    return RequestSchema(
        config=config,
        columns=columns,
        date_from=date_from,
        date_to=date_to,
        secrets=secrets,
    )


def _get_field(fields: Mapping[str, Any], field_name: str, required: bool, err_template: str) -> Any:
    try:
        return fields[field_name]
    except KeyError:
        if required:
            raise ValidationError(err_template.format(field_name=field_name))

    return None


def _get_query_param(fields: Mapping[str, str], field_name: str, required: bool = True) -> Optional[str]:
    return _get_field(fields, field_name, required, err_template='Query parameter `{field_name}` is required')


def _get_body_field(fields: Mapping[str, Any], field_name: str) -> Any:
    return _get_field(fields, field_name, required=True, err_template='Field `{field_name}` is required')


def _get_column_field(fields: Mapping[str, str], field_name: str, col_number: int) -> str:
    err_template = f'Field `{{field_name}}` is required for column {col_number}'
    return _get_field(fields, field_name, required=True, err_template=err_template)


def _get_payload(params: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    if payload := params.get('payload'):
        try:
            return json.loads(payload)
        except JSONDecodeError:
            raise ValidationError('Query parameter `payload` has bad format (must be JSON)')

    return None


def _validate_origin(origin: str) -> None:
    url = urlparse(origin)
    if url.netloc.endswith('.getconduit.app') or url.netloc.startswith('localhost:'):
        return

    raise ValidationError(f'Bad origin: {origin}')


def _parse_columns(columns: list[dict[str, Any]]) -> list[DataColumnSchema]:
    parsed_columns = []
    for col_number, col in enumerate(columns, 1):
        title = _get_column_field(col, 'title', col_number)
        type_key = _get_column_field(col, 'type', col_number)
        kind_key = _get_column_field(col, 'kind', col_number)
        agg_key = _get_column_field(col, 'agg', col_number)

        parsed_columns.append(
            DataColumnSchema(
                title=title,
                type=ColumnType[type_key],
                kind=ColumnKind[kind_key],
                agg=AggregationType[agg_key],
            ),
        )
    return parsed_columns
