from app import app
from config import Config
from logger import init_root_logger
from server import ExcelApplication, CustomGunicornLogger, ACCESS_FORMAT, GUNICORN_LEVEL

init_root_logger()


def run_app():
    options = {
        'bind': f'{Config.SERVER_HOST}:{Config.SERVER_PORT}',
        'workers': Config.GUNICORN_WORKER_COUNT,
        'threads': Config.GUNICORN_WORKER_THREADS,
        'timeout': Config.GUNICORN_TIMEOUT,
        'reload': Config.GUNICORN_RELOAD,
        'worker_class': 'sync',
        'logger_class': CustomGunicornLogger,
        'access_log_format': ACCESS_FORMAT,
        'loglevel': GUNICORN_LEVEL,
        'accesslog': '-',
        'errorlog': '-'
    }
    ExcelApplication(app, options=options).run()


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    run_app()
