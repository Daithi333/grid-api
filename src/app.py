from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from context import init_db_session, teardown_db_session
from error import (
    NotFoundError, BadRequestError, UnauthorizedError, handle_not_found, handle_bad_request,
    handle_unauthorized, handle_invalid_route, handle_internal_exception
)
from routes import files, cache, views, lookups, transactions, users, permissions

app = Flask(__name__)
app.register_blueprint(files)
app.register_blueprint(cache)
app.register_blueprint(views)
app.register_blueprint(lookups)
app.register_blueprint(transactions)
app.register_blueprint(users)
app.register_blueprint(permissions)

app.register_error_handler(NotFoundError, handle_not_found)
app.register_error_handler(BadRequestError, handle_bad_request)
app.register_error_handler(UnauthorizedError, handle_unauthorized)
app.register_error_handler(404, handle_invalid_route)
app.register_error_handler(500, handle_internal_exception)

CORS(app, resources={r"/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRES)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE_MB * 1024 * 1024  # 16 MB
jwt = JWTManager(app)


@app.get("/")
def read_root():
    return {"message": "ok"}


@app.before_request
def before_request():
    init_db_session()


@app.teardown_request
def teardown_request(exception=None):
    teardown_db_session()
