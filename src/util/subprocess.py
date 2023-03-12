import logging
import os
import subprocess

log = logging.getLogger(__name__)


def open_close_excel(input_file: str):
    """Open an excel it to re-evaluate formulas and cache results, then save and close. Expects .xlsx format."""
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

    except Exception:
        log.exception(f'Open-close file {input_file!r} - error')


# Old solution which works on windows. Could be made to work on MacOS with alternative to pythoncom, but not Linux

# def open_close_excel(path):
#     """Open and close excel to re-evaluate formula and cache results. Requires Excel installation on machine.
#     """
#     try:
#         pythoncom.CoInitialize()
#         excel_app = xlwings.App(visible=False)
#         excel_book = excel_app.books.open(path)
#         excel_book.save()
#         excel_book.close()
#         excel_app.quit()
#     except Exception:
#         traceback.print_exc()
