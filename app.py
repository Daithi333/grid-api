from flask import Flask
from flask_cors import CORS

from error import NotFoundError, BadRequestError, handle_not_found, handle_bad_request
from services.file_data import get_cache_summary
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


@app.get("/cache/summary")
def get_cache():
    return get_cache_summary()
