import pandas as pd
import os

from config.definitions import PROJECT_PATH, DATA_PATH
from elt.transform.preprocess import Preprocessor
# from ner_technos.ner_preprocessor import NERPreprocessor
# from ner_technos.train_model import NERTrainer
from elt.transform.process_technos import TechnosProcessor


def transform():
    preprocessor = Preprocessor(number_of_jobs=None)
    preprocessor.preprocess()
    # print('Preprocessed jobs :\n', preprocessor.jobs.head())

    techno_processor = TechnosProcessor(preprocessor.jobs)
    processed_jobs = techno_processor.process_technos()
    # print('Processed jobs (with technos) :\n', processed_jobs[['title', 'company', 'technos']][:10])

    processed_jobs.to_csv(os.path.join(DATA_PATH, 'processed.csv'))

# def run_ner():
    # preprocessor.jobs.to_csv(os.path.join(DATA_PATH, 'preprocessed_jobs.csv'))
    # jobs = pd.read_csv(os.path.join(DATA_PATH, 'preprocessed_jobs.csv'))
    
    # techno_recogniser = NERPreprocessor(preprocessor.jobs)
    # techno_recogniser.prepare_training()
    #
    # ner_trainer = NERTrainer()
    # ner_trainer.init_config()
    # ner_trainer.train()


# if __name__ == '__main__':
#
#     transform()
