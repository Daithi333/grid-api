## Demo Spreadsheet API

AG Grid [filter types](https://www.ag-grid.com/javascript-data-grid/filter-provided-simple/#simple-filter-options)

Built-in LRU cache does not allow delete or update one item by key, which is necessary for updating the excels and 
returning the new values.

[Roll your own LRU cache with ordered dict](https://pastebin.com/LDwMwtp8)

[Caching using a class](https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize)

[An implementation of LRU Cache](https://stackoverflow.com/posts/64816003/timeline)

[__call__ in python](https://www.geeksforgeeks.org/__call__-in-python/)

[Workbook to Bytes](https://stackoverflow.com/a/55144731/10554240)


### TODO
- user preferences - custom column widths, sort, etc
- formulas - re-evaluate after a programmatic save - complex issue as openpyxl and other libraries do not evaluate formulas,
  they simply read in a cached value from the last time the Excel was opened and saved. For now, if `EXCEL_AVAILABLE` flag is 
  set, the code will use xlwings library to silently open and close the excel, which will reevaluate. If not available, the 
  values of the formula cells will return empty. An alternative and more robust approach would be to always load the excel with 
  default setting of `data_only=False`, which will return the formulas, and then use formula library like pycel to evaluate the
  formula and then return the value in the row data as usual. 
  **Solved for now using xlwings to open and re-save the excel in the background, but only works if excel is available on the
  machine and env var `EXCEL_AVAILABLE` is set to `True`
- formulas - all formula columns need re-evaluated when a row is deleted
- improve row numbers handling - row numbers are not fixed, so deletions in one transaction will invalidate row numbers in
  other transactions. Better solution is needed, but for now it just iterates through previous rows to find a match.
- Add functionality for row insertions
