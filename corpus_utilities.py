import db_utilities
from os import walk
from ner_model import Ner
import main_db
import sqlite3


def corpus_configuration(config):
    """
    Initial corpus configuration
    :param config: config.ini
    :return: connection with database
    """
    corpus_db_name = config.get("Corpus", "corpus_file")
    corpus_path = config.get("Corpus", "path")
    file_ext = config.get("Corpus", "file_ext")
    file_start_en = config.get("Corpus", "file_start_en")
    file_start_pt = config.get("Corpus", "file_start_pt")

    if not db_utilities.check_db_file(corpus_db_name):
        corpus_setup_db(corpus_db_name, corpus_path, file_ext, file_start_pt, file_start_en, config)
    return db_utilities.connect_db(corpus_db_name)


def corpus_setup_db(corpus_db_name, corpus_path, file_ext, file_start_pt, file_start_en, config):
    """
    database configuration
    :param corpus_db_name: database name
    :param corpus_path: path to corpus files
    :param file_ext: file extension for corpus files
    :param file_start_pt: file name start for PT corpus files
    :param file_start_en: file name start for EN corpus files
    :param config: config.ini
    """
    connection = db_utilities.make_connection(corpus_db_name)
    make_tables(connection)
    annotate_corpus(connection, corpus_path, file_start_pt, file_start_en, file_ext, config)
    connection.close()


def annotate_corpus(connection, corpus_path,  file_start_pt, file_start_en, file_ext, config):
    """
    Annotates corpus with NER
    :param connection: corpus database connection
    :param corpus_path: path to corpus files
    :param file_start_pt: file name start for PT corpus files
    :param file_start_en: file name start for EN corpus files
    :param file_ext: file extension for corpus files
    :param config: config.ini
    """

    cursor = connection.cursor()

    ner = Ner(config)

    dirs = next(walk(corpus_path))[1]

    flag = True  # for development
    for directory in dirs:

        if flag:
            # flag = False  # for development, only adds one file

            path_pt = corpus_path + "/" + directory + "/" + file_start_pt + file_ext
            path_en = corpus_path + "/" + directory + "/" + file_start_en + file_ext

            with open(path_pt) as f:
                pt_text = f.read()
            with open(path_en) as f_en:
                en_text = f_en.read()

            inserted_pt_id = add_original_text(cursor, connection, pt_text)
            inserted_id = add_english(cursor, connection, en_text, inserted_pt_id)

            print("inserted id: " + str(inserted_id))

            # annotate text

            annotations = ner.mer_get_entities(en_text)  # names (dict keys)

            owl_id_annotations = main_db.get_owl_id(config, annotations)  # dict, text : [RIDs]

            # print("annotation from ner:")
            # print(annotations)
            for annot, owl_ids in owl_id_annotations.items():
                # print(str(annot) + " : " + str(owl_ids))
                add_annotation(cursor, connection, annot, owl_ids, inserted_id, "en")

    cursor.close()


def add_annotation(cursor, connection, annotation_text, annotation_ids, text_id, language):
    """
    add annotation to corpus database
    :param cursor: corpus database
    :param connection: corpus database
    :param annotation_text: annotation to insert
    :param annotation_ids: owl ids list for this annotation. can be more than one because synonym, pref_name, ...
    :param text_id: database id for which text does this annotation refer to
    :param language: pt or en
    """

    annotation = annotation_text

    for annot in annotation_ids:

        cursor.execute('''  
                            INSERT OR IGNORE INTO annotation (annotation, owl_id) VALUES (?, ?)
                             ''', (annotation, annot,))
        annot_id = cursor.lastrowid

        if language == "en":
            cursor.execute('''  
                            INSERT OR IGNORE INTO en_has_annotation (annotation, document) VALUES (?,?)
                             ''', (annot_id, text_id,))
        connection.commit()


def add_original_text(cursor, connection, text):
    """
    add text to corpus database
    :param cursor: corpus database
    :param connection: corpus database
    :param text: to insert in database
    :return: database id of inserted row
    """

    cursor.execute('''  
                        INSERT OR IGNORE INTO original_doc (original_text) VALUES (?)
                         ''', (text,))
    connection.commit()
    return cursor.lastrowid


def add_english(cursor, connection, text, inserted_pt_id):
    """
    add english text to corpus database
    :param cursor: corpus database
    :param connection: corpus database
    :param text: to insert in database
    :param inserted_pt_id: database id of previously inserted pt text, to which this text is a translation_model for
    :return: database id of inserted row
    """

    cursor.execute('''  
                        INSERT OR IGNORE INTO english_translation (original_text, en_text) VALUES (?,?)
                         ''', (inserted_pt_id, text,))
    connection.commit()
    return cursor.lastrowid


def make_tables(connection):
    """
    creates corpus tables
    :param connection: sqlite3 connection
    """

    cursor = connection.cursor()
    cursor.execute('''
                          DROP TABLE IF EXISTS original_doc
                          ''')

    cursor.execute('''
                          CREATE TABLE original_doc (
                          id     INTEGER PRIMARY KEY AUTOINCREMENT,
                          original_text   VARCHAR(100) UNIQUE
                          )''')

    cursor.execute('''
                          DROP TABLE IF EXISTS english_translation
                          ''')

    cursor.execute('''
                          CREATE TABLE english_translation (
                          id     INTEGER PRIMARY KEY AUTOINCREMENT,
                          original_text INTEGER NOT NULL,
                          en_text   VARCHAR(100) UNIQUE,
                          FOREIGN KEY (original_text) REFERENCES original_doc(id)
                          )''')

    cursor.execute('''
                          DROP TABLE IF EXISTS annotation
                          ''')

    cursor.execute('''
                          CREATE TABLE annotation (
                          id     INTEGER PRIMARY KEY AUTOINCREMENT,
                          annotation   VARCHAR(100),
                          owl_id VARCHAR(50) UNIQUE
                          )''')

    cursor.execute('''
                          DROP TABLE IF EXISTS en_has_annotation
                          ''')

    cursor.execute('''
                          CREATE TABLE en_has_annotation (
                          id     INTEGER PRIMARY KEY AUTOINCREMENT,
                          annotation INTEGER NOT NULL,
                          document INTEGER NOT NULL,
                          FOREIGN KEY (annotation) REFERENCES annotation(id),
                          FOREIGN KEY (document) REFERENCES english_translation(id)
                          )''')
    connection.commit()
    cursor.close()


def get_corpus_id_and_text(config):
    """
    retrieves corpus id and text from database
    :param config: config.ini
    :return: dict { corpus_en_id : text : corpus_en_text }
    """

    corpus_db_name = config.get("Corpus", "corpus_file")
    connection = db_utilities.make_connection(corpus_db_name)
    connection.row_factory = sqlite3.Row

    rows = connection.execute(''' SELECT id, en_text FROM english_translation''')

    corpus_dict = dict()

    for row in rows:
        corpus_dict[row[0]] = {'text': row[1]} # dict { corpus_en_id : text : corpus_en_text }

    connection.close()

    return corpus_dict


def get_entities_owl(config) -> list:
    """
    Retrieves annotated corpus owl ids from database
    :param config: config.ini
    :return: list of owl ids in all corpus
    """
    corpus_db_name = config.get("Corpus", "corpus_file")
    connection = db_utilities.make_connection(corpus_db_name)

    rows = connection.execute(''' SELECT owl_id FROM annotation''').fetchall()

    connection.close()

    return rows


def get_owl_annotations_en(connection_corpus, doc_id):
    """
    Retrieves owl ids for one document from database
    :param connection_corpus: sqlite3 connection
    :param doc_id: database internal doc id
    :return: list of owl ids for this doc_id
    """

    rows = connection_corpus.execute(''' SELECT owl_id FROM annotation, en_has_annotation
                              WHERE en_has_annotation.annotation=annotation.id
                              AND en_has_annotation.document = ?''', (doc_id,)).fetchall()

    return rows
