from csv import QUOTE_MINIMAL, DictWriter
from typing import Any, Iterable, Protocol

from conduit_sdk.common.schema import DATE_FORMAT, ColumnType, DataColumnSchema


class SupportsWrite(Protocol):
    def write(self, row: str) -> None:
        ...


def write_csv(target: SupportsWrite, columns: list[DataColumnSchema], rows: Iterable[dict[str, Any]]) -> None:
    column_titles = [col.title for col in columns]
    writer = DictWriter(target, fieldnames=column_titles, quoting=QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def convert_data_for_csv(row: dict[str, Any], columns: list[DataColumnSchema]) -> dict[str, str]:
    prepared_row = {}

    for col in columns:
        value = row[col.title]

        if col.type == ColumnType.BOOL:
            value = bool(value)
        elif col.type in (ColumnType.MONEY, ColumnType.DECIMAL, ColumnType.PERCENT):
            value = float(value)
            value = round(value, 4)
        elif col.type == ColumnType.INTEGER:
            value = int(value)
        elif col.type == ColumnType.DATE:
            value = value.strftime(DATE_FORMAT)

        prepared_row[col.title] = str(value)

    return prepared_row


def convert_rows_and_write_csv(
    target: SupportsWrite,
    columns: list[DataColumnSchema],
    rows: Iterable[dict[str, Any]],
) -> None:
    converted_rows = (convert_data_for_csv(row, columns) for row in rows)
    write_csv(target, columns=columns, rows=converted_rows)
