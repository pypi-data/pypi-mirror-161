from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
import json

from config.definitions import DB_STRING, DATA_PATH
from config.postgres_schema import RawJob, ProcessedJob, Base


def create_tables():
    engine = create_engine(DB_STRING, echo=True)

    Base.metadata.create_all(engine)
