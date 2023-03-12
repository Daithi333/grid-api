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
- formulas - re-evaluate after a programmatic save
- improve row numbers handling - row numbers are not fixed, so deletions in one transaction will invalidate row numbers 
  in other transactions. Better solution is needed, but for now it just iterates through previous rows to find a match.
- Add functionality for row insertions


### Run app

Build: `docker build \
          -t excel-app:local \
          -f docker/Dockerfile \
          .`

Add a `.env` to project root with necessary env variables

Run: `docker run --rm -p 5000:5000 --env-file ./.env --name excel-app excel-app:local`

Create docker volume to persist db data `docker volume create pgdata`
