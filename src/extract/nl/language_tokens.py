import os

from lexnlp.extract.common.language_dictionary_reader import LanguageDictionaryReader


class NlLanguageTokens:
    abbreviations = {'nr.', 'abs.', 'no.', 'act.', 'inc.', 'p.', 'Inc.'}
    articles = ['de', 'het', 'een']
    conjunctions = ['en', 'of']

    @staticmethod
    def init():
        abr_file_path = os.path.join(os.path.dirname(__file__),
                                     'data/abbreviations.txt')
        if os.path.isfile(abr_file_path):
            file_set = LanguageDictionaryReader.read_str_set(abr_file_path)
            NlLanguageTokens.abbreviations = \
                NlLanguageTokens.abbreviations.union(file_set)

NlLanguageTokens.init()
