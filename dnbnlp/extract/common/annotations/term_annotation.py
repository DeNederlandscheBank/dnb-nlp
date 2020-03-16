from typing import Tuple, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.utils.map import Map


class TermAnnotation(TextAnnotation):
    record_type = 'solvency 2 term'
    """
    """
    def __init__(self,
                 coords: Tuple[int, int],
                 locale: str = 'en',
                 text: str = None,
                 name: str = None,
                 alias: str = None,
                 name_en: str = None,
                 source: str = None,
                 category: str = None,
                 id: int = None,
                 priority: int = None):
        super().__init__(
            name=name,
            locale=locale,
            coords=coords,
            text=text)
        self.alias = alias
        self.name_en = name_en
        self.source = source
        self.category = category
        self.id = id
        self.priority = priority

    def get_cite_value_parts(self) -> List[str]:
        parts = [str(self.name or ''),
                 str(self.year or '')]
        return parts

    def get_dictionary_values(self) -> dict:
        df = Map({
            'tags': {
                'Extracted Entity Name': self.name,
                'Extracted Entity Text': self.text
            }
        })
        if self.year:
            df.tags['year'] = self.year
        return df
