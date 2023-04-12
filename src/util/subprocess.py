import logging
import os
import subprocess
from sys import platform

from config import Config

log = logging.getLogger(__name__)


def open_close_excel(input_file: str):
    if platform == "linux" or platform == "linux2":
        _open_close_libre(input_file)
    elif platform == "darwin" or platform == "win32":
        _open_close_excel(input_file, platform)
    else:
        raise NotImplementedError


def _open_close_libre(input_file: str) -> bool:
    """Open an excel it to re-evaluate formulas and cache results, then save and close. Expects .xlsx format."""
    if not Config.LO_AVAILABLE:
        log.warning(f'Unable to open-close file {input_file!r} as LibreOffice is not available')
        return False

    try:
        log.info(f'Open-close file {input_file!r} - begin')
        input_dir, input_filename = os.path.split(input_file)
        temp_filename = os.path.splitext(input_filename)[0] + ".ods"
        temp_file = os.path.join(input_dir, temp_filename)

        # Open the input file in headless mode, triggering the caching of formula results, and save as ODS format
        command = ["libreoffice", "--headless", "--calc", "--convert-to", "ods", input_file, "--outdir", input_dir]
        log.info(f'Running command: {command}')
        subprocess.run(command, check=True)

        # Convert the ODS file to XLSX format
        command = ["libreoffice", "--headless", "--convert-to", "xlsx", temp_file, "--outdir", input_dir]
        log.info(f'Running command: {command}')
        subprocess.run(command, check=True)

        os.remove(temp_file)
        log.info(f'Open-close file {input_file!r} - complete')
        return True

    except Exception:
        log.exception(f'Open-close file {input_file!r} - error')
        return False


def _open_close_excel(input_file, platform_: str) -> bool:
    """Open and close excel to re-evaluate formula and cache results. Requires Excel installation on machine."""
    if not Config.EXCEL_AVAILABLE:
        log.warning(f'Unable to open-close file {input_file!r} as MS Excel is not available')
        return False

    try:
        import xlwings
        if platform_ == 'win32':
            import pythoncom
            pythoncom.CoInitialize()
        excel_app = xlwings.App(visible=False)
        excel_book = excel_app.books.open(input_file)
        excel_book.save()
        excel_book.close()
        excel_app.quit()
        return True
    except Exception:
        log.exception(f'Open-close file {input_file!r} - error')
        return False
