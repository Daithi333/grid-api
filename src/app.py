from datetime import timedelta

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import init_db_session, teardown_db_session
from logger import init_root_logger
from services import file_cache
from error import NotFoundError, BadRequestError, handle_not_found, handle_bad_request
from routes import files, views, lookups, transactions, users

init_root_logger()

app = Flask(__name__)
app.register_blueprint(files)
app.register_blueprint(views)
app.register_blueprint(lookups)
app.register_blueprint(transactions)
app.register_blueprint(users)

app.register_error_handler(NotFoundError, handle_not_found)
app.register_error_handler(BadRequestError, handle_bad_request)

CORS(app, resources={r"/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRES)
jwt = JWTManager(app)


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


@app.before_request
def before_request():
    init_db_session()


@app.teardown_request
def teardown_request(exception=None):
    teardown_db_session()
