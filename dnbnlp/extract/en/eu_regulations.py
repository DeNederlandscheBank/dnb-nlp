"""Regulation extraction for English.

This module implements regulation extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

# Imports
import regex as re

from typing import Generator

from lexnlp.extract.common.annotations.regulation_annotation import RegulationAnnotation

REGULATION_CODES_MAP = {}

REGULATION_PTN = r"""
(
	(Directive(s)?)\s+
    (
      (\s+(and|to|or|-|\,)\s+)?
  	  (\d+\/\d+\/(EC|EEC|EU))
    )+
|
  (Regulation(s)?)\s+
    (
      (\s+(and|to|or|-|\,)\s+)?
      \((EC|EEC|EU)\)\s+NO\s+\d+\/\d+
    )+
|
  ((that|this|these|those)\s+(Directive(s)?|Regulation(s)?))
| 
  the\s+Solvency\s+(II|2)\s+Directive
)
"""

ARTICLE_PTN = r"""
(
	(
		Article(s)?\s+
      (
        (\s+(and|to|or|-|\,)\s+)?
        (
          (\d+([a-z])?)+((\s+paragraph\s+)?\s+\((\d+|[a-z]+|\d+[a-z]+)\))*
        |
          ((\s+paragraph\s+)?\s+\((\d+|[a-z]+|\d+[a-z]+)\))+
        )
      
      )+
  )
|
  (
    (that|this|these|those)\s+Article(s)?
  )
)"""

ARTICLE_PTN_RE = re.compile(ARTICLE_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

DIRECTIVE_PTN_RE = re.compile(REGULATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

REGULATION_PTN_RE = re.compile(ARTICLE_PTN + r'\sof\s'+ REGULATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

REGULATIONS_DICT_KEYS = ['regulation_type', 'regulation_code', 'regulation_str']

def get_regulations(text, return_source=False, as_dict=False) -> Generator:
    """
    Get regulations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """
    for ant in get_regulation_annotations(text):
        if not as_dict:
            item = (ant.source, ant.name, ant.coords)
            if return_source:
                item += (ant.text,)
            yield item
        else:
            yield ant.to_dictionary_legacy()


def get_regulation_annotations(text: str) -> \
        Generator[RegulationAnnotation, None, None]:
    """
    Get regulations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """

    for match in ARTICLE_PTN_RE.finditer(text):

        source_text = match.groups()

        item = source_text

        ant = RegulationAnnotation(coords=match.span(),
                                   source="Legislation (European Union)",
                                   name="".join(source_text[0]),
                                   text=source_text[0].strip())
        yield ant        
  
    for match in DIRECTIVE_PTN_RE.finditer(text):

        source_text = match.groups()

        item = source_text

        ant = RegulationAnnotation(coords=match.span(),
                                   source="Legislation (European Union)",
                                   name="".join(source_text[0]),
                                   text=source_text[0].strip())
        yield ant        

    for match in REGULATION_PTN_RE.finditer(text):

        source_text = match.groups()

        item = source_text

        ant = RegulationAnnotation(coords=match.span(),
                                   source="Legislation (European Union)",
                                   name="".join(source_text[0]),
                                   text=source_text[0].strip())
        yield ant

