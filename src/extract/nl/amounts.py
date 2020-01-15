"""Amount extraction for Dutch.

This module implements basic amount extraction functionality in Dutch.

This module supports converting:
- numbers with comma delimiter: "25,000.00", "123,456,000"
- written numbers: "Seven Hundred Eighty"
- mixed written numbers: "5 million" or "2.55 BILLION"
- written ordinal numbers: "twenty-fifth"
- fractions (non written): "1/33", "25/100"; where 1 < numerator < 99; 1 < denominator < 999
- fraction No/100 wil be treated as 00/100
- written numbers and fractions: "twenty one AND 5/100"
- written fractions: "one-third", "three tenths", "ten ninety-ninths", "twenty AND one-hundredths",
  "2 hundred and one-thousandth";
   where 1 < numerator < 99 and 2 < denominator < 99 and numerator < denominator;
   or 1 < numerator < 99 and denominator == 100, i.e. 1/99 - 99/100;
   or 1 < numerator < 99 and denominator == 1000, i.e. 1/1000 - 99/1000;
- floats starting with "." (dot): ".5 million"
- "dozen": "twenty-two DOZEN"
- "half": "Six and a HALF Billion", "two and a half"
- "quarter": "five and one-quarter", "5 and one-quarter", "three-quartes"
- multiple numbers: "$25,400, 1 million people and 3.5 tons"

Avoids:
- skip: "5.3.1.", "1/1/2010"
"""

# pylint: disable=bare-except

# Imports
import string
from typing import Generator

import nltk
import regex as re
from num2words import num2words

from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation


# Define small numbers
SMALL_NUMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                 20, 30, 40, 50, 60, 70, 80, 90]
SMALL_NUMBERS_MAP = {num2words(n, lang = "nl"): n for n in SMALL_NUMBERS}
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True, lang = "nl"): n for n in SMALL_NUMBERS})
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True, lang = "nl") + 's': n for n in SMALL_NUMBERS[3:20]})
SMALL_NUMBERS_MAP.update({num2words(n, lang = "nl"): n for n in SMALL_NUMBERS[20:]})

UNIQUE_NUMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                          20, 30, 40, 50, 60, 70, 80, 90,
                          100, 1000, 1000000, 1000000000, 1000000000000]
UNIQUE_NUMBERS_MAP = {num2words(n, ordinal=True, lang = "nl").replace('een ', ''): n
                      for n in UNIQUE_NUMBERS}
UNIQUE_NUMBERS_MAP.update(
    {num2words(n, lang = "nl").replace('een ', ''): n for n in UNIQUE_NUMBERS})
UNIQUE_NUMBERS_MAP.update(
    {'één': 1,
     'een': 1,
     'eenhalf': 0.5,
     'miljoen': 1000000,
     'miljoenste': 1000000,
     'miljard': 1000000000,
     'miljardste': 1000000000})

unique_number_list = list(UNIQUE_NUMBERS_MAP.keys())
unique_number_list.sort(key=len, reverse=True)
UNIQUE_NUMBER_SPLIT_RE = re.compile(r'({}|\s+)'.format('|'.join(unique_number_list)))

BIG_NUMBERS_EXPONENT = [3, 6, 9, 12]
MAGNITUDE_MAP = {num2words(10 ** n, lang = "nl").replace("een ", ""): 10 ** n for n in BIG_NUMBERS_EXPONENT}
MAGNITUDE_MAP.update(
    {'triljoen': 1000000000000000,
     'biljoen' : 1000000000000,
     'miljard' : 1000000000,
     'miljoen' : 1000000,
     'duizend' : 1000})

small_numbers = list(SMALL_NUMBERS_MAP.keys())
small_numbers.sort(key=len, reverse=True)
big_numbers = list(MAGNITUDE_MAP.keys())
big_numbers.sort(key=len, reverse=True)

CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "¥": "JPY",
    "£": "GBP",
    "₠": "EUR",
    "₨": "INR",
    "₹": "INR",
    "₺": "TRY",
    "元": "CNY",
    "₽": "RUB",
    # "¢": None,
    "₩": "KRW",
}
CURRENCY_PREFIX_MAP = {
    "chf": "CHF",
    "rmb": "CNY",
}
allowed_prev_units = list(CURRENCY_SYMBOL_MAP) + list(CURRENCY_PREFIX_MAP)

fraction_smb_to_value = {
    '½': 1.0/2, '⅓': 1.0/3, '⅔': 2.0/3,
    '¼': 1.0/4, '¾': 3.0/4, '⅕': 1.0/5,
    '⅖': 2.0/5, '⅗': 3.0/5, '⅘': 4.0/5,
    '⅙': 1.0/6, '⅚': 5.0/6, '⅐': 1.0/7,
    '⅛': 1.0/8, '⅜': 3.0/8, '⅝': 5.0/8,
    '⅞': 7.0/8, '⅑': 1.0/9, '⅒': 1.0/10
}
fraction_smb_to_string = {k: str(fraction_smb_to_value[k])[1:]
                          for k in fraction_smb_to_value}

fraction_symbols = ''.join([k for k in fraction_smb_to_value])
FRACTION_TAIL = rf'\s{{0,2}}[{fraction_symbols}]+'
FRACTION_TAIL_RE = re.compile(FRACTION_TAIL,
                              re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

 
NUM_PTN = r"""
(?:(?:(?:(?:(?:[\.\d][\d\.,]*\s*|\W|^)
(?:(?:{written_small_numbers}|{written_big_numbers}
|honderd(?:ste(?:en)?)?|dozijn|en|een\s+halve|een\s?half|een\s?kwart|kwart)[\s-]*)+)
(?:(?:no|\d{{1,2}})/100)?)|(?<=\W|^)(?:[\.\d][\d\.,/]*))(?:\W|$))(?:{fraction_tail})*""".format(
    written_small_numbers='|'.join(small_numbers),
    written_big_numbers='|'.join(big_numbers),
    fraction_tail=FRACTION_TAIL)

NUM_PTN_RE = re.compile(NUM_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

NON_WRIT_RE = re.compile(r'[\d\.]+')
MIXED_WRIT_RE = re.compile(r'(^[\d\.]*)(.+)', re.DOTALL)
ONLY_BIG_WRIT_RE = re.compile(r'^\s*(?:{}|honderd|dozijn)'.format('|'.join(MAGNITUDE_MAP)))
NUM_FRACTION_RE = re.compile(r'(\s+no|\d{1,2})/(\d{1,3}[^/])')
NUM_FRACTION_SUB_RE = re.compile(r'(?:\s*en)?(?:\s+no|\s*\d{1,2})/\d{1,3}')
HALF_RE = re.compile(r'en\s?een\s?half')
QUARTER_RE = re.compile(r'(?:\s*en\s+)?(een|twee|drie)\s*kwart')

AND_RE = re.compile(r'\W*en\W*', re.IGNORECASE | re.MULTILINE | re.DOTALL)

FRACTION_PTN = r"(?:(?:\W|^)" \
               r"(?:een[\s-]+(?:{writ_ord_2_90}|tiende|honderdste|duizendste|(?:{writ_20_90})[\s-]+" \
               r"(?:{writ_ord_1_9})))|" \
               r"(?:(?:{writ_1_90}|[\s-]+)+[\s-]+(?:{writ_ord_3_90_pl}|tiende|honderdste|duizendste" \
               r"(?:{writ_20_90})[\s-]+(?:{writ_ord_1_9_pl}))))" \
               r"(?:\W|$)".format(writ_ord_2_90='|'.join([num2words(n, ordinal=True, lang = "nl") for n in SMALL_NUMBERS[2:]]),
                                  writ_20_90='|'.join([num2words(n, lang = "nl") for n in SMALL_NUMBERS[20:]]),
                                  writ_ord_1_9='|'.join([num2words(n, ordinal=True, lang = "nl") for n in SMALL_NUMBERS[1:10]]),
                                  writ_1_90='|'.join([num2words(n, lang = "nl") for n in SMALL_NUMBERS[1:]]),
                                  writ_ord_3_90_pl='|'.join([num2words(n, ordinal=True, lang = "nl") + 's'
                                                             for n in SMALL_NUMBERS[3:]]),
                                  writ_ord_1_9_pl='|'.join([num2words(n, ordinal=True, lang = "nl") + 's'
                                                            for n in SMALL_NUMBERS[1:10]]))
FRACTION_PTN_RE = re.compile(FRACTION_PTN)

FRACTION_EXTRACT_PTN = r"((?:(?:{writ})|(?:(?:{writ_20_90})[\s-]+(?:{writ_1_9}))))[\s-]+" \
                       r"((?:{writ_ord_mix}|(?:(?:{writ_20_90})[\s-]+" \
                       r"(?:{writ_ord_1_9_mix}))|honderdste?|duizendste?))" \
    .format(writ='|'.join([num2words(n, lang = "nl") for n in SMALL_NUMBERS[1:]]),
            writ_20_90='|'.join([num2words(n, lang = "nl") for n in SMALL_NUMBERS[20:]]),
            writ_1_9='|'.join([num2words(n, lang = "nl") for n in SMALL_NUMBERS[1:10]]),
            writ_ord_mix='|'.join([num2words(n, ordinal=True, lang = "nl") + 's?' for n in SMALL_NUMBERS[2:]]),
            writ_ord_1_9_mix='|'.join([num2words(n, ordinal=True, lang = "nl") + 's?' for n in SMALL_NUMBERS[1:10]]))
FRACTION_EXTRACT_PTN_RE = re.compile(FRACTION_EXTRACT_PTN, re.S | re.M)

wnl = nltk.stem.WordNetLemmatizer()

# Taken from Su Nam Kim Paper...
grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""
chunker = nltk.RegexpParser(grammar)

def split(text):
    return [i for i in UNIQUE_NUMBER_SPLIT_RE.split(text) if i not in ['', ' ']]

def text2num(s, search_fraction=True):
    """
    Convert written amount into integer/float.
    :param s: written number
    :param search_fraction: extract fraction
    :return: integer/float
    """

    n = 0
    g = 0
    s = s.lower().replace('.', '').replace(',', '.').replace('-', ' ').strip(string.whitespace).rstrip(
        string.punctuation + string.whitespace)
    s = re.sub(r'\s+en\s*$|^\s*en\s+', '', s)
    if not (s.startswith('.') and s[1].isdigit()):
        s = s.lstrip(string.punctuation + string.whitespace)
    if s in ['k', 'm', 'b']:
        return
    # if only number or float in string
    if NON_WRIT_RE.fullmatch(s):
        return float(s)

    # if written number has integer/float prefix: "25 million", "2.035 thousand tons"
    if not NUM_FRACTION_RE.fullmatch(s):
        p, s = MIXED_WRIT_RE.search(s).groups()
        g = float(p) if p else 0

    # if written big number has no prefix: "lovely million", "a dozen"
    if ONLY_BIG_WRIT_RE.search(s) and not g:
        s = 'één ' + s

    d = 0
    dnd = NUM_FRACTION_RE.search(s)
    fs = FRACTION_PTN_RE.search(s)
    q = QUARTER_RE.search(s)
    h = HALF_RE.search(s)
    if h:
        s = HALF_RE.sub('', s)
        d = 0.5
    elif q:  # convert quarters
        s = QUARTER_RE.sub('', s)
        nu = q.groups()[0]
        d = text2num(nu) / 4
    elif dnd:  # if text has fraction like 1/33 or 87/100 or 1/100
        dn, dd = dnd.groups()
        if dn.isdigit():
            d = int(dn) / int(dd)
        s = NUM_FRACTION_SUB_RE.sub('', s)
    elif fs and search_fraction:  # extract written fractions
        try:
            s = FRACTION_PTN_RE.sub('', s)
            fe = fs.group(0)
            fn, fd = FRACTION_EXTRACT_PTN_RE.search(fe).groups()
            fn = text2num(fn, search_fraction=False)
            fd = text2num(fd, search_fraction=False)
            d = fn / fd
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    # process
    a = split(s)

    x1 = 0
    for w in a:
        if w in ['een', 'en']:
            continue
        x = SMALL_NUMBERS_MAP.get(w, None)
        if x is not None:
            g += x
        elif 'honderd' in w and g != 0:
            g *= 100
        elif w == 'dozijn' and g != 0:
            g *= 12
        elif (w == 'half') or (w == 'halve'):
            if x1:
                g += x1 * .5
            else:
                g += .5
        else:
            x = x1 = MAGNITUDE_MAP.get(w, None)
            if x is not None:
                n += g * x
                g = 0
            else:
                raise RuntimeError('Unknown number: ' + w)

    return n + g + d


def get_np(text) -> Generator:
    tokens = nltk.word_tokenize(text)
    pos_tokens = nltk.tag.pos_tag(tokens)
    chunks = chunker.parse(pos_tokens)
    for subtree in chunks.subtrees(filter=lambda t: t.label() == 'NP'):
        np = ' '.join([i[0] for i in subtree.leaves()])
        _np = ' '.join([wnl.lemmatize(i[0]) for i in subtree.leaves()])
        yield np, _np


def get_amounts(text: str,
                return_sources=False,
                extended_sources=True,
                float_digits=4) -> Generator[float, None, None]:
    """
    Find possible amount references in the text.
    :param text: text
    :param return_sources: return amount AND source text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    for ant in get_amount_annotations(text, extended_sources, float_digits):  # type: AmountAnnotation
        if return_sources:
            yield (ant.value, ant.text)
        else:
            yield ant.value


def get_amount_annotations(text: str,
                           extended_sources=True,
                           float_digits=4) \
        -> Generator[AmountAnnotation, None, None]:
    """
    Find possible amount references in the text.
    :param text: text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    for match in NUM_PTN_RE.finditer(text):
        found_item = match.group()
        fract_tail_items = FRACTION_TAIL_RE.finditer(found_item)
        for fract_tail in fract_tail_items:
            fract_tail_smb = fract_tail.group().strip(' ')
            if fract_tail_smb in fraction_smb_to_string:
                fract_ending = fraction_smb_to_string[fract_tail_smb]
                found_item = found_item[:fract_tail.span()[0]]
                found_item += fract_ending
            break

        if AND_RE.fullmatch(found_item):
            continue
        try:
            amount = text2num(found_item)
        except:
            continue
        if amount is None:
            continue
        if isinstance(amount, float) and float_digits:
            amount = round(amount, float_digits)

        if extended_sources:
            unit = ''
            next_text = text[match.span()[1]:]
            if next_text:
                for np, _ in get_np(next_text):
                    if next_text.startswith(np):
                        unit = np
                if unit:
                    found_item = ' '.join([found_item.strip(), unit])
            if not unit:
                prev_text = text[:match.span()[0]]
                prev_text_tags = nltk.word_tokenize(prev_text)
                if prev_text_tags and prev_text_tags[-1].lower() in allowed_prev_units:
                    sep = ' ' if text[match.span()[0] - 1] == ' ' else ''
                    found_item = sep.join([prev_text_tags[-1], found_item.rstrip()])

            ant = AmountAnnotation(coords=match.span(),
                                   value=amount,
                                   text=found_item.strip())
            yield ant
        else:
            ant = AmountAnnotation(coords=match.span(),
                                   value=amount,
                                   text=match.group())
            yield ant
