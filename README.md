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
- user preferences for Grid view - custom column widths, saved sort, etc
- improve row numbers handling - row numbers are not fixed, so deletions in one transaction will invalidate row numbers 
  in other transactions. Better solution is needed, but for now it just iterates through previous rows to find a match.
- Add functionality for row insertions
- More testing of data changes, and multiple transactions which will undoubtedly cause problems with row numbers
- Cache could just cache the file data and not the openpyxl cells


### Run app

#### Docker

 - Add a `.env` to project root with necessary env variables

 - Build: `docker build -t excel-app:local -f docker/Dockerfile .`

 - Run: `docker run --rm -p 5000:5000 --env-file ./.env --name excel-app excel-app:local`


#### Docker compose

 - Create docker volume to persist db data `docker volume create pgdata`

 - Use `docker-compose build` or `docker-compose up`



### Unit Tests

 - To run the test suite, use `pytest src/tests -v`

 - To run coverage report, use `pytest --cov=src --cov-config=.coveragerc src/` 
   or `pytest --cov=src --cov-config=.coveragerc --cov-report=html src/` for html report
