import similarity_model
from ner_model import Ner
import corpus_utilities
import main_db


class Configuration:
    """
    Configures different modules necessary
    """
    corpus_cursor = ''
    similarity_connection = ''
    main_db_connection = ''

    def __init__(self, config):
        self.similarity_connection = similarity_model.similarity_configuration(config)
        ner = Ner(config)
        ner.ner_configuration(config)
        self.main_db_connection = main_db.configuration(config)
        self.corpus_cursor = corpus_utilities.corpus_configuration(config)





