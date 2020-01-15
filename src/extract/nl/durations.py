"""Duration extraction for Dutch.

This module implements duration extraction functionality in Dutch.

"""

import regex as re
from typing import Generator, List

from lexnlp.extract.common.durations.durations_parser import DurationParser
from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation

from src.extract.nl.amounts import AmountParserNL

amounts_parser = AmountParserNL()
get_amounts = amounts_parser.parse


class NlDurationParser(DurationParser):
    DURATION_MAP = {
        "second": 1 / (60 * 60 * 24),
        "minute": 1 / (60 * 24),
        "hour": 1 / 24,
        "day": 1,
        "week": 7,
        "month": 30,  # 365.25/12.,
        "quarter": 365 / 4,
        "year": 365,  # 365.25,
        "annum": 365,
        "anniversary": 365,
        "anniversaries": 365
    }

    DURATION_TRANSLATION_MAP = {
        "seconde": 'second',
        "seconden": 'second',
        "minuut": 'minute',
        "minuten": 'minute',
        "uur": 'hour',
        "uren": 'hour',
        "dag": 'day',
        "dagen": 'day',
        "week": 'week',
        "weken": 'week',
        "maand": 'month',
        "maanden": 'month',
        "kwartaal": 'quarter',
        "kwartalen": 'quarter',
        "jaar": 'year',
        "jaren": 'year',
    }

    duration_items = sorted(DURATION_TRANSLATION_MAP.keys(), key=len, reverse=True)
    duration_items_joined = '|'.join(duration_items)
    DURATION_MAP_RE = re.compile(duration_items_joined)

    DURATION_PTN = r"""
    (?P<text>
        (?P<num_text>{num_ptn})?
        (?P<unit_prefix>(?:kalender|levens))?
        (?P<unit_name>{unit_names})
    )
    (?:\W|$)
    """.format(num_ptn=amounts_parser.NUM_PTN, unit_names=duration_items_joined)

    DURATION_PTN_RE = re.compile(DURATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

    INNER_CONJUNCTIONS = ['en', 'plus']

    INNER_PUNCTUATION = re.compile(r'[\s\,]')

    LOCALE = 'nl'

    @classmethod
    def get_all_annotations(cls,
                            text: str,
                            float_digits=4) \
            -> List[DurationAnnotation]:

        all_annotations = []
        for match in cls.DURATION_PTN_RE.finditer(text):
            capture = match.capturesdict()
            amount_text = ''.join(capture.get('num_text', ''))
            amounts = list(get_amounts(amount_text, float_digits=float_digits))
            if len(amounts) != 1:
                amount = 1
            else:
                amount = amounts[0]
            unit_name_local = ''.join(capture.get('unit_name', '')).lower()
            unit_prefix = ''.join(capture.get('unit_prefix', '')).lower()
            unit_name_local = cls.DURATION_MAP_RE.findall(unit_name_local)
            if not unit_name_local:
                continue
            unit_name_local = unit_name_local[0]
            unit_name_en = cls.DURATION_TRANSLATION_MAP.get(unit_name_local)

            amount_days = cls.DURATION_MAP[unit_name_en] * amount
            if float_digits:
                amount_days = round(amount_days, float_digits)
            ant = DurationAnnotation(coords=match.span(),
                                     text=''.join(capture.get('text', '')),
                                     amount=amount,
                                     duration_days=amount_days,
                                     duration_type_en=unit_name_en,
                                     duration_type=unit_name_local,
                                     prefix=unit_prefix,
                                     locale=cls.LOCALE)
            all_annotations.append(ant)
        return all_annotations


def get_durations(text: str, float_digits=4) -> Generator:
    for ant in NlDurationParser.get_annotations(text, float_digits):
        yield dict(
                location_start=ant.coords[0],
                location_end=ant.coords[1],
                source_text=ant.text,
                unit_name_local=ant.duration_type,
                unit_name=ant.duration_type_en,
                unit_prefix=ant.prefix,
                amount=ant.amount,
                amount_days=ant.duration_days)


def get_duration_annotations(text: str,
                             float_digits=4) \
        -> Generator[DurationAnnotation, None, None]:
    yield from NlDurationParser.get_annotations(text, float_digits)


def get_duration_annotations_list(text: str,
                                  float_digits=4) \
        -> List[DurationAnnotation]:
    return NlDurationParser.get_annotations(text, float_digits)


def get_duration_list(text: str, float_digits=4):
    return list(get_durations(text, float_digits))
