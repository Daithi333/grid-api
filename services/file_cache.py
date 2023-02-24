import io
from typing import List

from openpyxl import load_workbook
from openpyxl.cell import ReadOnlyCell

from util.LRU import LRUCache
from config import Config
from database.models import File


class FileCache(LRUCache):

    def __init__(self, func):
        super().__init__(func, maxsize=Config.FILE_CACHE_SIZE)

    def _generate_key(*args, **kwargs) -> hash:
        func = args[0]
        file = args[1]
        file_id = str(file.id) if isinstance(file, File) else file
        return str(file_id)


# @lru_cache(maxsize=Config.FILE_CACHE_SIZE)
@FileCache
def load_excel(file: File) -> List[List[ReadOnlyCell]]:
    file_bytes = io.BytesIO(file.blob)
    wb = load_workbook(file_bytes, read_only=True, data_only=True)
    ws = wb.active  # only get single (first) worksheet for now
    return list(ws.rows)[:]


def summary() -> dict:
    return load_excel.summary()


def remove(file_id: str) -> bool:
    return load_excel.remove(file_id)


def clear() -> bool:
    load_excel.clear()
    return True


def keys() -> List[str]:
    return load_excel.keys()
