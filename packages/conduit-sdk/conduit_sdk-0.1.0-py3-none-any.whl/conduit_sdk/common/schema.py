from dataclasses import dataclass
from enum import Enum

DATE_FORMAT = '%Y-%m-%d'


class ColumnType(str, Enum):
    STRING = 'STRING'
    DATE = 'DATE'
    DECIMAL = 'DECIMAL'
    MONEY = 'MONEY'
    INTEGER = 'INTEGER'
    PERCENT = 'PERCENT'
    BOOL = 'BOOL'


class ColumnKind(str, Enum):
    DIMENSION = 'DIMENSION'
    METRIC = 'METRIC'


class AggregationType(str, Enum):
    SUM = 'SUM'
    COUNT = 'COUNT'
    AVERAGE = 'AVERAGE'
    MAX = 'MAX'
    MIN = 'MIN'
    UNIQ = 'UNIQ'


@dataclass
class DataColumnSchema:
    title: str
    type: ColumnType  # noqa: A003
    kind: ColumnKind
    agg: AggregationType
