import io
from functools import lru_cache
from typing import List, Union, Tuple

from openpyxl import load_workbook
from openpyxl.cell import ReadOnlyCell

from database import db
from database.models import File
from error import NotFoundError


class FileData:

    @classmethod
    def get_data(cls, file_id: str):
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
