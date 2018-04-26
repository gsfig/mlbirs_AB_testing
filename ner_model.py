import utilities
import json
import rdflib
import re
import os.path
import shutil
from subprocess import Popen, PIPE


class Ner:
    """
    Named entity recognition
    """
    lexicon = ''

    def __init__(self, config):
        self.lexicon = config.get('NER', 'lexicon_file')

    def ner_configuration(self, config):
        """
        configures NER
        :param config: config.ini
        """

        if not utilities.check_file(self.lexicon):
            owl_names_extract = config.get('Predicates', 'to_extract')
            file = config.get('Files', 'rdf_file')
            to_remove = config.get('Predicates', 'subject_to_remove')

            self. create_lexicon_file(self.lexicon, file, owl_names_extract, to_remove)
            self.mer_data_file(self.lexicon)

    def mer_data_file(self, lexicon_file):
        """
        Makes MER internal data files.
        :param lexicon_file: txt file with lexicon
        """

        print("mer produce data files")

        command = "bash"
        produce_data_files_command = "produce_data_files.sh"

        sreturn = ''
        # have to copy lexicon file to data folder
        file_from = os.path.abspath(lexicon_file)
        file_to = os.path.abspath('MER/data')
        just_file = os.path.basename(lexicon_file)

        shutil.copy(file_from, file_to)
        # print("file_to: " + str(file_to) + ", lexicon: " + lexicon + ", basename: " + just_file)
        with Popen([command, produce_data_files_command, just_file], cwd='MER', stdout=PIPE, bufsize=1,
                   universal_newlines=True) as process:
            for line in process.stdout:  # b'\n', b'\r\n', b'\r' are recognized as newline
                sreturn += line

        #print("RETURN PRODUCE DATA FILES: " + str(sreturn))

    def mer_get_entities(self, text):
        """
        identifies entities according to lexicon
        :param text: text to identify
        :return: list with one entity per line (name)
        """
        lexicon_file = self.lexicon
        command1 = "bash"
        get_entities_command = "get_entities.sh"
        just_file = os.path.basename(lexicon_file)
        file = os.path.splitext(just_file)[0]

        sreturn = ''
        with Popen([command1, get_entities_command, text, file], cwd='MER', stdout=PIPE, bufsize=1,
                   universal_newlines=True) as process:
            for line in process.stdout:  # b'\n', b'\r\n', b'\r' are recognized as newline
                sreturn += line

        entities_and_freqs = self.get_entities_and_frequencies(sreturn)

        # print(entities_and_freqs)

        return list(entities_and_freqs.keys())

    def get_entities_and_frequencies(self, mer_response):
        """
        Get all annotated term and number of occurrences
        :param mer_response: first column corresponds to the start-index, the second to the end-index and the third to the annotated term
        :return: dict {entity : frequency}
        """

        entities = dict()

        split1 = mer_response.split('\n')  # each line

        for s in split1:
            s2 = s.split('\t')  # index \t index \t term
            if len(s2) > 1:
                entity = s2[2]
                entity.lower()  # TODO: Lower case
                if entity in entities:
                    entities[entity] += 1
                else:
                    entities[entity] = 1
        return entities

    def create_lexicon_file(self, lexicon_file, file, owl_names_extract, to_remove):
        """
        Produces text file with one term per line
        :param lexicon_file: final file
        :param file: owl / rdf file
        :param owl_names_extract: owl predicates to extract
        :param to_remove: owl tags to remove
        """
        print("NER: creating lexicon from database")
        pred_list = json.loads(owl_names_extract)
        data = dict()
        g = rdflib.Graph()
        g.load(file)
        for subject, predicate, obj in g:
            for tag in pred_list:
                if tag in predicate:
                    s = self.remove_string(str(subject), to_remove)
                    o = self.remove_string(str(obj), to_remove)
                    self.add_to_lexicon(data, s, o, tag)
        self.write_lexicon_file(data, lexicon_file)

    def write_lexicon_file(self, data, lexicon_file):
        """
        writes dictionary to file as long list. Only extracts owl children
        :param data: dict data
        :param lexicon_file: file to write
        """

        print("writing " + str(lexicon_file) + " file")
        filewrite = open(lexicon_file, "w")
        out = list()

        for rid in data:
            for tag in data[rid]:
                for item in data[rid][tag]:
                    out.append(item)
        out.sort()
        for s in out:
            filewrite.write(s)
            filewrite.write("\n")
        filewrite.close()

    def add_to_lexicon(self, data, subject, obj, tag):
        """
        temporary dict to make sure no duplicates are added
        :param data: main dict to add s, p, o
        :param subject: owl subject
        :param obj: owl object
        :param tag: owl tag
        """
        if subject in data:
            o = data.get(subject)
        else:
            o = dict()

        if tag not in o:
            o[tag] = list()

        # remove " and ' characters
        s = re.sub('["]', '', obj)
        if s.startswith("'"):
            s = re.sub('[\']', '', s)

        o[tag].append(s)
        data[subject] = o

    def remove_string(self, to_edit, to_remove):
        """
        Auxiliar function
        :param to_edit:
        :param to_remove:
        :return:
        """
        return to_edit.replace(to_remove, '')
