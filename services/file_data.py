import io
from functools import lru_cache
from typing import List, Union, Tuple

from openpyxl import load_workbook
from openpyxl.cell import ReadOnlyCell

from database import db
from database.models import File
from error import NotFoundError, BadRequestError
from models.data_filter import DataFilter, RowFilter


class FileData:

    @classmethod
    def get_data(cls, file_id: str, limit: int, offset: int):
        cells = load_excel(file_id)

        row_data = []
        for row_number, row_cells in enumerate(cells[1:]):
            row = {'_rowNumber': row_number + 1}
            for i, hc in enumerate(cells[0]):
                row[hc.value] = row_cells[i].value
            row_data.append(row)

        return {
            'columnDefs': cls._get_column_definitions(cells),
            'rowData': row_data
        }

    @classmethod
    def _get_column_definitions(cls, cells) -> List[dict]:
        """Get ag-grid column properties based on openpyxl data_types"""

        data_type_props = {
            'n': {'filter': 'agNumberColumnFilter'},
            's': {'filter': 'agTextColumnFilter'},
            'd': {'filter': 'agDateColumnFilter'},
            'f': {'filter': 'agNumberColumnFilter', 'editable': False},
            'e': {'filter': 'agNumberColumnFilter', 'editable': False}
        }

        data_types = cls._get_column_data_types(cells)

        column_definitions = []
        for i, hc in enumerate(cells[0]):
            column_def = {'field': hc.value, 'colId': hc.column_letter, **data_type_props[data_types[i]]}
            if data_types[i] in ['e', 'f']:
                column_def['headerName'] = column_def['field'] + '*'
            column_definitions.append(column_def)

        return column_definitions

    @classmethod
    def _get_column_data_types(cls, cells) -> List[str]:
        """Return list of column data types based on the first populated row in each column."""
        data_types = [cell.data_type if cell.value else None for cell in cells[1]]

        for col_index, data_type in enumerate(data_types):
            if data_type is not None:
                continue

            data_types[col_index] = 'n'  # default to 'n' as openpyxl does, in case entire column is empty
            for row_cells in cells[2:]:
                if row_cells[col_index].value is not None:
                    data_types[col_index] = row_cells[col_index].data_type
                    break

        return data_types

    @classmethod
    def get_filtered_data(cls, file_id: str, limit: int, offset: int, data_filter: DataFilter):
        cells = load_excel(file_id)

        filtered_cells = cls._apply_column_filter(cells, data_filter.columns)
        header_cells, row_cells = cls._apply_row_filters(filtered_cells, data_filter.rows)

        limited_row_cells = row_cells[offset:offset+limit]

        headers: List[str] = [c.value for c in header_cells]
        rows = [[c.value for c in r] for r in limited_row_cells]

        return {
            'headers': encode_row(headers),
            'rows': encode(rows),
            'count': len(limited_row_cells),
            'total': len(row_cells)
        }

    @classmethod
    def _apply_column_filter(
            cls, cells: List[List[ReadOnlyCell]], column_filter: List[str]
    ) -> List[List[ReadOnlyCell]]:
        """Filter 2D array of cells based on column filter. First row in cells expected to be the column headers"""
        if not column_filter:
            return cells

        filtered_cells = []
        # filter header cells first and record their row indices
        kept_column_indices = []
        header_cells = []
        for i, hc in enumerate(cells[0]):
            if hc.value in column_filter:
                kept_column_indices.append(i)
                header_cells.append(hc)

        filtered_cells.append(header_cells)

        # filter rows based on which columns are being kept
        for row in cells[1:]:
            row_cells: List[ReadOnlyCell] = []
            for i, rc in enumerate(row):
                if i in kept_column_indices:
                    row_cells.append(rc)
            filtered_cells.append(row_cells)

        return filtered_cells

    @classmethod
    def _apply_row_filters(
            cls, cells: List[List[ReadOnlyCell]], row_filters: List[RowFilter]
    ) -> Tuple[List[ReadOnlyCell], List[List[ReadOnlyCell]]]:
        """Filter the cells based on the row filters and return headers and row separately for further processing"""
        def include_row(row: List[ReadOnlyCell], column_index: int, value: str, operator: str) -> bool:
            if operator == '==':
                return row[column_index].value == value
            elif operator == '!=':
                return row[column_index].value != value
            elif operator == '>':
                return row[column_index].value > value
            elif operator == '<':
                return row[column_index].value < value
            elif operator == '>=':
                return row[column_index].value >= value
            elif operator == '<=':
                return row[column_index].value <= value
            else:
                raise BadRequestError(f'Operator {operator!r} not supported')

        header_cells = cells[0]
        header_cell_values = [c.value for c in header_cells]
        row_cells_per_row = cells[1:]
        for row_filter in row_filters:
            try:
                col_index = header_cell_values.index(row_filter.column)
            except ValueError:
                raise BadRequestError(
                    f'Row filter cannot be applied as column {row_filter.column!r} it is not included in column filter'
                )
            row_cells_per_row = [
                row for row in row_cells_per_row
                if include_row(row, col_index, row_filter.value, row_filter.operator)
            ]

        return header_cells, row_cells_per_row


@lru_cache(maxsize=50)
def load_excel(file_id: str) -> List[List[ReadOnlyCell]]:
    with next(db.get_session()) as session:
        file = session.query(File).filter_by(id=file_id).one_or_none()
    if not file:
        raise NotFoundError(f'File {file_id!r} not found')

    file_bytes = io.BytesIO(file.blob)
    wb = load_workbook(file_bytes, read_only=True, data_only=True)
    ws = wb.active  # only get single (first) worksheet for now
    return list(ws.rows)[:]


def get_cache_summary() -> dict:
    cache_info = load_excel.cache_info()
    return {
        'hits': cache_info.hits,
        'misses': cache_info.misses,
        'maxsize': cache_info.maxsize,
        'currsize': cache_info.currsize,
    }


def encode(rows: List[List[str]]):
    return [encode_row(r) for r in rows]


def encode_row(row: List[Union[str, float, int]]):
    row = [str(el) if el is not None else '' for el in row]
    return ','.join(row)
