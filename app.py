from flask import Flask, request
from flask_cors import CORS

from services import file_cache
from error import NotFoundError, BadRequestError, handle_not_found, handle_bad_request
from routes import files, views, lookups, transactions

app = Flask(__name__)
app.register_blueprint(files)
app.register_blueprint(views)
app.register_blueprint(lookups)
app.register_blueprint(transactions)
app.register_error_handler(NotFoundError, handle_not_found)
app.register_error_handler(BadRequestError, handle_bad_request)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.get("/")
def read_root():
    return {"message": "ok"}


@app.get("/cache")
def get_cache_summary():
    return file_cache.summary()


@app.delete("/cache")
def clear_from_cache():
    file_id = request.args.get('id')
    if file_id:
        success = file_cache.remove(file_id)
        message = f'File {file_id} cleared from file cache' if success else 'File not in cache'
    else:
        success = file_cache.clear()
        message = 'File cache cleared'

    return {'success': success, 'message': message}

