from sqlmodel import create_engine as ce
from sqlalchemy_utils import database_exists, create_database


def create_engine(addr: str):
    engine = ce(addr)
    if not database_exists(engine.url):
        print(f"database {engine.url} does not exist, create now")
        create_database(engine.url)
    return engine
