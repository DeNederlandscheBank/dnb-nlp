import os

from lexnlp.extract.common.language_dictionary_reader import LanguageDictionaryReader


class NlLanguageTokens:
    abbreviations = {'nr.', 'abs.', 'no.', 'act.', 'inc.', 'p.', 'Inc.'}
    articles = ['een', 'de', 'het']
    conjunctions = ['en', 'of', 'alsof', 'maar', 'doch', 'noch', 'dus', 'derhalve', 
                    'daardoor', 'daarom', 'doordat', 'door', 'terwijl', 'omdat', 
                    'aangezien', 'want', 'daar', 'dewijl', 'doordien', 'naardien', 
                    'nademaal', 'overmits', 'vermits', 'wijl', 'indien', 'ingeval', 
                    'zo', 'zodat', 'opdat', 'sinds', 'sedert', 'nadat', 'dat']
    pronouns = {'ik', 'hij', 'zij', 'we', 'jij', 'zij'}

    @staticmethod
    def init():
        abr_file_path = os.path.join(os.path.dirname(__file__),
                                     'data/abbreviations.txt')
        if os.path.isfile(abr_file_path):
            file_set = LanguageDictionaryReader.read_str_set(abr_file_path)
            NlLanguageTokens.abbreviations = \
                NlLanguageTokens.abbreviations.union(file_set)

        prn_file_path = os.path.join(os.path.dirname(__file__),
                                     'data/pronouns.txt')
        if os.path.isfile(prn_file_path):
            file_set = LanguageDictionaryReader.read_str_set(prn_file_path)
            NlLanguageTokens.pronouns = \
                NlLanguageTokens.pronouns.union(file_set)


NlLanguageTokens.init()
