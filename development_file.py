from os.path import isfile
from os import remove


def development(config):
    """
    for development purpose
    :param config:
    :return:
    """

    # mer data files
    lexicon_file = config.get('NER', 'lexicon_file')
    path = 'MER/data/'

    # if isfile(lexicon_file):  # if delete db_file => delete corpus_db
    #     remove(lexicon_file)
    #
    # if isfile(path + lexicon_file):
    #     remove(path + lexicon_file)
    #     remove(path + 'lexicon_radlex_word1.txt')
    #     remove(path + 'lexicon_radlex_word2.txt')
    #     remove(path + 'lexicon_radlex_word2.txt')
    #     remove(path + 'lexicon_radlex_words2.txt')

    # corpus
    # corpus_db_name = config.get("Corpus", "corpus_file")
    # if isfile(corpus_db_name):
    #     remove(corpus_db_name)

    # main DB
    # main_db_name = config.get("MainDB", "db_file")
    # if isfile(main_db_name):
    #     remove(main_db_name)


def tests(configuration):
    """
    for development purpose
    :param configuration:
    :return:
    """

    main_db_connection = configuration.main_db_connection
    dishin_db = configuration.similarity_connection

    # 1. main_db owl_ids exist but not pref_name or synonym or obsolete.

    entity_ids = set(main_db_connection.execute('SELECT id FROM entity ').fetchall())
    synonym_fk = set(main_db_connection.execute('SELECT fkentity FROM Synonym ').fetchall())
    pref_name_fk = set(main_db_connection.execute('SELECT fkentity FROM Preferred_name ').fetchall())
    pref_name_obs_fk = set(main_db_connection.execute('SELECT fkentity FROM Preferred_Name_for_Obsolete ').fetchall())

    id_set = synonym_fk | pref_name_fk
    id_set2 = id_set | pref_name_obs_fk

    print(len(entity_ids))
    print(len(id_set2))

    diff = list(entity_ids - id_set2)
    print(len(diff))
    diff_owls = dict()
    for d in diff:
        rows = main_db_connection.execute('SELECT owl_id FROM entity WHERE id = ?', (d,)).fetchall()
        diff_owls[d] = rows

    print(diff_owls)

    exit()


def get_response():
    file = open("testfile.txt", "r")

    reply = file.read()
    file.close()
    return reply
