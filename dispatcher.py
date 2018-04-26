import json
import development_file # development purposes: tests, etc.
import configparser
from configuration import Configuration
from translation_serv import TranslationService
from ner_model import Ner
import similarity_model
from math import floor


def dispatcher(query: str):
    """
    Main backend function
    :param query: User query
    :return: json ready response to html
    """
    # print("dispatcher")
    # print("query: " + str(query))

    # 0. configurations, database and files creation
    config = configparser.ConfigParser()
    config.read('config.ini')

    # development_file.development(config)

    c = Configuration(config)

    # development_file.tests(c)

    # 1. Translate query
    translation = TranslationService()
    translated = translation.translate_query(query, "pt", "en")
    if len(query) == 0:
        translated = "pulmonary"
    # print(translated)

    # 2. query NER (Name Entity Recognition)
    ner = Ner(config)
    entities = ner.mer_get_entities(translated)

    if len(entities) < 1:
        print("no entities by NER")
        return json.dumps({})

    # 3. find similar
    #similar_dict = similarity_model.get_similar(config, entities) # dict { corpus_en_id : text, resnik dishin, resnik mica, lin mica }
    # print(similar_dict)

    # 4. organize response
    #response = organize_response(similar_dict)

    response2 = development_file.get_response()

    return response2
    #return json.dumps(response)


def organize_response(full_dict):
    """
    Reduces dict to another dict with only necessary information for html response. Chooses which score (resnik dishin,
    resnik mica, lin mica) to show.
    :param full_dict: dict with all information: { corpus_en_id : text, resnik dishin, resnik mica, lin mica }
    :return: dict {doc_id, doc_text, average_score}
    """
    doc_and_ave = dict()
    for doc in full_dict:
        temp = dict()
        temp['doc_id'] = doc
        temp['doc_text'] = full_dict[doc]['text']
        temp['average_score'] = floored_percentage(full_dict[doc]['lin_mica'], 3)
        #print("val: " + str(full_dict[doc]['resnik_dishin']) + " %: " + str(temp['average_score']))
        doc_and_ave[doc] = temp
    return doc_and_ave


def floored_percentage(val, digits):
    """
    helper function to get percentage of average
    :param val: score from similarity evaluation
    :param digits: number of decimal places
    :return:
    """
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}'.format(digits, floor(val) / 10 ** digits)


