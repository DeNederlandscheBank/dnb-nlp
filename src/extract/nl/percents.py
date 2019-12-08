import regex as re
from typing import Generator

from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation

from src.extract.nl.amounts import AmountParserNL

amounts_parser = AmountParserNL()
get_amounts = amounts_parser.parse

PERCENT_UNITS_MAP = {
    'procent': 0.01,
    '%': 0.01
}

PERCENT_PTN = r"""
(?P<text>(?P<num_text>{num_ptn})\s*(?P<unit_name>\w*procent|%))(?:\W|$)
""".format(num_ptn=amounts_parser.NUM_PTN)
PERCENT_PTN_RE = re.compile(PERCENT_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_percents(text: str, float_digits=4) -> Generator:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    for ant in get_percent_annotations(text, float_digits):
        yield dict(
                location_start = ant.coords[0],
                location_end = ant.coords[1],
                source_text = ant.text,
                unit_name = ant.sign,
                amount = ant.amount,
                real_amount = ant.fraction)

def get_percent_annotations(text: str, float_digits = 4) -> \
        Generator[PercentAnnotation, None, None]:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    for match in PERCENT_PTN_RE.finditer(text):
        capture = match.capturesdict()
        amount_text = ''.join(capture.get('num_text', ''))
        unit_name = ''.join(capture.get('unit_name', ''))
        amount = list(get_amounts(amount_text, float_digits=float_digits))
        if len(amount) != 1:
            continue
        else:
            amount = amount[0]
        if 'procent' in unit_name.lower():
            unit_name = 'procent'
        real_amount = PERCENT_UNITS_MAP.get(unit_name, 0) * amount
        if float_digits:
            real_amount = round(amount, float_digits)
        ant = PercentAnnotation(coords=match.span(),
                                text=''.join(capture.get('text', '')),
                                sign=unit_name,
                                amount=amount,
                                fraction=real_amount,
                                locale='nl')
        yield ant


# def get_percent_list(*args, **kwargs):
#     return list(get_percents(*args, **kwargs))
