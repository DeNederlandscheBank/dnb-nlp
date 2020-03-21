"""Token parsing for Dutch.

This module implements token parsing, such as tokens, stems, and lemma tokenization functionality in Dutch.

Todo:
No wordnet implemented
No lemmatizer functions implemented
"""

# Imports
import os
import pickle
from typing import List, Generator

# NLTK imports
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
 
# Stopwords (using standard nltk stopwords)
STOPWORDS = set(stopwords.words('dutch'))

# # Collocations
# COLLOCATION_SIZE = 10000
# BIGRAM_COLLOCATIONS = pickle.load(
#     open(os.path.join(MODULE_PATH, "collocation_bigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))
# TRIGRAM_COLLOCATIONS = pickle.load(
#     open(os.path.join(MODULE_PATH, "collocation_trigrams_{0}.pickle".format(COLLOCATION_SIZE)), "rb"))

# Setup default stemmer for Dutch
DEFAULT_STEMMER = nltk.stem.snowball.DutchStemmer()


def get_tokens(text, lowercase=False, stopword=False, preserve_line=True) -> Generator:
    """
    Get token generator from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param preserve_line: keep the preserve the sentence and not sentence tokenize it.
    :return:
    """
    if stopword:
        for token in nltk.word_tokenize(text, preserve_line=preserve_line):
            if token.lower() in STOPWORDS:
                continue
            if lowercase:
                yield token.lower()
            else:
                yield token
    else:
        for token in nltk.word_tokenize(text, preserve_line=preserve_line):
            if lowercase:
                yield token.lower()
            else:
                yield token


def get_token_list(text: str, lowercase: bool = False, stopword: bool = False,
                   preserve_line: bool = True) -> List:
    """
    Get token list from text.
    :param text:
    :param lowercase:
    :param stopword:
    :param preserve_line: keep the preserve the sentence and not sentence tokenize it.
    :return:
    """
    return list(get_tokens(text, lowercase=lowercase, stopword=stopword,
                           preserve_line=preserve_line))


def get_stems(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER) -> Generator:
    """
    Get stems from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.
    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    for token in get_tokens(text, lowercase=lowercase, stopword=stopword):
        yield stemmer.stem(token)


def get_stem_list(text, lowercase=False, stopword=False, stemmer=DEFAULT_STEMMER) -> List:
    """
    Get stems materialized from text.
    N.B.: when stemmer is SnowballStemmer, lowercase is always returned no matter the parameter.

    :param text:
    :param lowercase:
    :param stopword:
    :param stemmer:
    :return:
    """
    return list(get_stems(text, lowercase=lowercase, stopword=stopword, stemmer=stemmer))
