import os
from config.definitions import PROJECT_PATH


class NERTrainer:
    def __init__(self, language='en'):
        self.language = language
        self.pipeline = "tok2vec,ner"
        self.config_file = os.path.join(PROJECT_PATH, 'etl/transform/ner_technos' ,f'{language}_config.cfg')
        self.train_data_path = os.path.join(PROJECT_PATH, 'etl/transform/data/train_data')
        self.model_output_path = os.path.join(PROJECT_PATH, f'etl/transform/data/model_{language}')

    def init_config(self):
        os.system(f'python3 -m spacy init config {self.config_file} --pipeline {self.pipeline} '
                  f'--lang {self.language} --force ')

    def train(self):
        os.system(f'python3 -m spacy train {self.config_file} --output {self.model_output_path} '
                  f'--paths.train {self.train_data_path}/train_data.spacy '
                  f'--paths.dev {self.train_data_path}/valid_data.spacy')


