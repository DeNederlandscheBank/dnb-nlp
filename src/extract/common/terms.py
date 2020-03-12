"""Term extraction for Dutch.
"""

from typing import List, Tuple, Union, Dict, Generator, Any

from lexnlp.extract.common.annotations.text_annotation import TextAnnotation

from src.extract.common.annotations.term_annotation import TermAnnotation
from src.extract.common.dict_terms import find_dict_terms, conflicts_take_first_by_id, \
    prepare_alias_blacklist_dict, conflicts_top_by_priority, term_config, add_aliases_to_term


_ALIAS_BLACK_LIST_PREPARED = prepare_alias_blacklist_dict([])


def get_terms(text: str,
              term_config_list: List[Tuple[int, str, List[Tuple[str, str, bool, int]]]],
              priority: bool = False,
              priority_by_id: bool = False,
              language: str = None,
              min_alias_len: int = 2,
              prepared_alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]]
              = _ALIAS_BLACK_LIST_PREPARED) -> Generator[Tuple[Tuple, Tuple], Any, Any]:
    """
    Searches for geo entities from the provided config list and yields pairs of (entity, alias).
    Entity is: (entity_id, name, [list of aliases])
    Alias is: (alias_text, lang, is_abbrev, alias_id)

    This method uses general searching routines for dictionary entities from dict_entities.py module.
    Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
    entity_alias(), add_aliases_to_entity().
    :param text:
    :param geo_config_list: List of all possible known geo entities in the form of tuples
    (id, name, [(alias, lang, is_abbrev, alias_id), ...]).
    :param priority: If two entities found with the totally equal matching aliases -
    then use the one with the greatest priority field.
    :param priority_by_id: If two entities found with the totally equal matching aliases -
    then use the one with the lowest id.
    :param text_languages: Language(s) of the source text. If a language is specified then only aliases of this
    language will be searched for. For example: this allows ignoring "Island" - a German language
     alias of Iceland for English texts.
    :param min_alias_len: Minimal length of geo entity aliases to search for.
    :param prepared_alias_black_list: List of aliases to exclude from searching in the form:
     dict of lang -> (list of normalized non-abbreviation aliases, list of normalized abbreviation aliases).
     Use dict_entities.prepare_alias_blacklist_dict() for preparing this dict.
    :return: Generates tuples: (entity, alias)
    """
    conflict_resolving_func = None

    if priority_by_id:
        conflict_resolving_func = conflicts_take_first_by_id

    if priority:
        conflict_resolving_func = conflicts_top_by_priority

    for ent in find_dict_terms(text,
                               term_config_list,
                               conflict_resolving_func=conflict_resolving_func,
                               language=language,
                               min_alias_len=min_alias_len,
                               prepared_alias_black_list=prepared_alias_black_list):
        yield ent.entity


def get_term_annotations(text: str,
                         term_config_list: List[Tuple[int, str, List[Tuple[str, str, bool, int]]]],
                         priority: bool = False,
                         priority_by_id: bool = False,
                         language: str = None,
                         min_alias_len: int = 2,
                         prepared_alias_black_list: Union[None, Dict[str, Tuple[List[str], List[str]]]]
                         = _ALIAS_BLACK_LIST_PREPARED) -> Generator[TermAnnotation, None, None]:

    conflict_resolving_func = None

    if priority_by_id:
        conflict_resolving_func = conflicts_take_first_by_id

    if priority:
        conflict_resolving_func = conflicts_top_by_priority

    dict_entries = find_dict_terms(text,
                                     term_config_list,
                                     conflict_resolving_func=conflict_resolving_func,
                                     language=language,
                                     use_stemmer=True,
                                     min_alias_len=min_alias_len,
                                     prepared_alias_black_list=prepared_alias_black_list)

    for ent in dict_entries:
        ant = TermAnnotation(coords=ent.coords)
        if ent.term[0]:
            ant.name = ent.term[0][1]
            ant.category = ent.term[0][2]
            ant.alias = ent.term[0][4]
        yield ant


def load_terms_dict_by_path(terms_fn: str, use_stemmer: bool = False):
    
    terms = {}

    import csv

    with open(terms_fn, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            terms[row['id']] = term_config(row['id'], row['name'], row['category'], int(row['priority']) if row['priority'] else 0,
                                                name_is_alias=False)
            term = terms.get(row['entity_id'])
            add_aliases_to_term(term,
                                row['english name'],
                                'en',
                                row['type'] == 'abbreviation', use_stemmer = use_stemmer)
            add_aliases_to_term(term,
                                row['dutch name'],
                                'nl',
                                row['type'] == 'abbreviation', use_stemmer = use_stemmer)

    # with open(aliases_fn, 'r', encoding='utf8') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         term = terms.get(row['entity_id'])
    #         if term:
    #             add_aliases_to_term(term,
    #                                   row['alias'],
    #                                   row['locale'],
    #                                   row['type'].startswith('iso') or row['type'] == 'abbreviation', use_stemmer = use_stemmer)

    return terms.values()
