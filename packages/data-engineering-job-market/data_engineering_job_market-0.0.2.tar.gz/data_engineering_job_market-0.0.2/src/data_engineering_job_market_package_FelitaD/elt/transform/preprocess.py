import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine
from langdetect import detect

from config.definitions import DB_STRING


class Preprocessor:

    def __init__(self, number_of_jobs):
        # connect to postgres database
        self.engine = create_engine(DB_STRING)
        # retrieve raw data into a dataframe
        self.jobs = pd.read_sql('raw_jobs', self.engine)
        # limit length of data for testing
        if number_of_jobs:
            self.jobs = self.jobs[:number_of_jobs]

    def preprocess(self):
        self.jobs.drop('id', axis=1, inplace=True)
        self.jobs = self.jobs.convert_dtypes()
        self.jobs['created_at'] = pd.to_datetime(self.jobs['created_at'])
        self.jobs['remote'].replace('N', np.nan, inplace=True)
        self.jobs['title'] = self.jobs['title'].apply(lambda x: self.preprocess_title(x))
        self.jobs['language'] = self.jobs['text'].apply(lambda x: detect(x))
        self.jobs.drop(self.jobs[(self.jobs['language'] != 'en') & (self.jobs['language'] != 'fr')].index, axis=0, inplace=True)
        self.jobs['text'] = self.jobs['text'].apply(lambda x: self.preprocess_text(x))
        self.jobs.reset_index(inplace=True, drop=True)

    @staticmethod
    def preprocess_title(title):
        # Remove (H/F), H/F, H / F, (F/H), F/H, (M/F), M/F, (F/M), F/M, M/W, (HF),(M/F/D), (F/H/X), (m/f/d), (m/w/d), (H/S/T)
        gender_regex = '[\(]?[HFMWDXmfdwST]{1}[\s]?[\/]{1}[\s]?[HFMWDXmfdwST]{1}[\)]?[\/]?[HFMWDXmfdwST]?[\)]?'
        title = re.sub(gender_regex, '', title)
        # Remove empty parenthesis
        title = re.sub('\([\s]?\)', '', title)
        # Remove | #
        title = re.sub('[|#]', '', title)
        title = title.strip()
        return title

    @staticmethod
    def preprocess_text(text):
        # Remove newline at beginning of text
        text = re.sub('^[\\]n[\s]*', '', text)
        # Remove \xa0 (non-breaking space in Latin1 ISO 8859-1)
        text = text.replace(u'\xa0', u' ')
        # Replace newlines if there is more than 3
        text = re.sub('[\s]{3,10}', '\n\n', text)
        return text
