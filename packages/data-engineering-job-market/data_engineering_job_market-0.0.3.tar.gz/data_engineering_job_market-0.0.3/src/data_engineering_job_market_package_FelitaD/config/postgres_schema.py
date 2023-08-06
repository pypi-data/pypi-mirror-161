from numpy.random._generator import Sequence
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, inspect, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

Base = declarative_base()


class RawJob(Base):
    __tablename__ = 'raw_jobs'

    id = Column(Integer, primary_key=True)
    url = Column(String(400), nullable=False, unique=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    industry = Column(String(100))
    location = Column(String(100))
    remote = Column(String(100))
    type = Column(String(20))
    created_at = Column(Date)
    text = Column(String)


class ProcessedJob(Base):
    __tablename__ = 'processed_jobs'

    id = Column(Integer, primary_key=True)
    url = Column(String(400), nullable=False, unique=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    industry = Column(String(100))
    stack = Column(String(100))
    location = Column(String(100))
    remote = Column(String(100))
    type = Column(String(20))
    language = Column(String(2))
    created_at = Column(Date)
    text = Column(String)


class PivottedJob(Base):
    __tablename__ = 'pivotted_jobs'

    id = Column(Integer, primary_key=True)
    url = Column(String(400), nullable=False, unique=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100))
    type = Column(String(100))
    industry = Column(String(100))
    remote = Column(String(100))
    created_at = Column(Date)
    language = Column(String(2))
    technos = Column(String(100))
