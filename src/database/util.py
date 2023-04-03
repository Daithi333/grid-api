import shortuuid
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def db_exists(url: str):
    try:
        engine = create_engine(url)
        conn = engine.connect()
        conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{engine.url.database}'")
        conn.close()

    except OperationalError as e:
        print(e)
        parts = url.rsplit('/', 1)
        url, dbname = parts[0], parts[1]
        engine = create_engine(url)
        conn = engine.connect()
        conn.execute(f"CREATE DATABASE {dbname}")
        conn.close()


def generate_uuid() -> str:
    return str(shortuuid.uuid())
