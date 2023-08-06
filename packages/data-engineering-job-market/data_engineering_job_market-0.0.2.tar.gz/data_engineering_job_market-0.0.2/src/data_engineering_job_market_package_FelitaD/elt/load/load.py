import os
import pandas as pd
import ast
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
import json

from config.definitions import DB_STRING, DATA_PATH
from config.postgres_schema import PivottedJob, Base


def run_loader(**context):
    loader = Loader()
    loader.load()

    context['ti'].xcom_push(
        key='length_jobs',
        value=len(loader.jobs)
    )


class Loader:

    def __init__(self):
        self.jobs = pd.read_csv(os.path.join(DATA_PATH, 'pivotted.csv'))

    def load(self):
        engine = create_engine(DB_STRING, echo=True)
        db_session = sessionmaker(bind=engine)

        Base.metadata.create_all(engine)
        Base.metadata.bind = engine

        for i in range(len(self.jobs)):
            url = self.jobs.loc[i, 'url']
            title = self.jobs.loc[i, 'title']
            company = self.jobs.loc[i, 'company']
            location = self.jobs.loc[i, 'location']
            _type = self.jobs.loc[i, 'type']
            industry = self.jobs.loc[i, 'industry']
            remote = self.jobs.loc[i, 'remote']
            created_at = self.jobs.loc[i, 'created_at']
            language = self.jobs.loc[i, 'language']
            technos = self.jobs.loc[i, 'technos']

            job = PivottedJob(url=url,
                              title=title,
                              company=company,
                              location=location,
                              type=_type,
                              industry=industry,
                              remote=remote,
                              created_at=created_at,
                              language=language,
                              technos=technos)

            with engine.connect() as connection:
                with db_session(bind=connection) as session:
                    session.begin()
                    try:
                        session.merge(job)
                        session.commit()
                    except:
                        session.rollback()
