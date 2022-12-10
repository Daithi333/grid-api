from dataclasses import dataclass
from typing import List


@dataclass
class RowFilter:
    column: str
    operator: str
    value: str
    index: int


@dataclass
class DataFilter:
    columns: List[str]
    rows: List[RowFilter]
