from typing import List

from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
#from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

from src.extract.nl.durations import get_duration_list, get_duration_annotations
from src.extract.nl.tests.test_amounts import AssertionMixin


class TestGetDurations(AssertionMixin):
    def test_duration_prefix(self):
        text = "Als iemand het veertiende levensjaar of het vijfentwintigste levensjaar bereikt in het derde kalenderjaar;"
        res = get_duration_list(text=text)
        self.assertCountEqual(res, [{'location_start': 14,
                                     'location_end': 37,
                                     'source_text': ' veertiende levensjaar',
                                     'unit_name_local': 'jaar',
                                     'unit_name': 'year',
                                     'unit_prefix': 'levens',
                                     'amount': 14.0,
                                     'amount_days': 5110.0},
                                    {'location_start': 43,
                                     'location_end': 72,
                                     'source_text': ' vijfentwintigste levensjaar',
                                     'unit_name_local': 'jaar',
                                     'unit_name': 'year',
                                     'unit_prefix': 'levens',
                                     'amount': 25.0,
                                     'amount_days': 9125.0},
                                    {'location_start': 86,
                                     'location_end': 106,
                                     'source_text': ' derde kalenderjaar',
                                     'unit_name_local': 'jaar',
                                     'unit_name': 'year',
                                     'unit_prefix': 'kalender',
                                     'amount': 3.0,
                                     'amount_days': 1095.0}])

    def test_written_duration(self):
        text = 'sinds vijfentwintig jaar'
        res = get_duration_list(text=text)
        self.assertCountEqual(res, [{'location_start': 5,
                                     'location_end': 24,
                                     'source_text': ' vijfentwintig jaar',
                                     'unit_name_local': 'jaar',
                                     'unit_name': 'year',
                                     'unit_prefix': '',
                                     'amount': 25.0,
                                     'amount_days': 9125.0}])

        ants = list(get_duration_annotations(text=text))
        self.assertEqual((5, 24), ants[0].coords)
        self.assertEqual('vijfentwintig jaar', ants[0].text.strip())
        self.assertEqual('jaar', ants[0].duration_type)
        self.assertEqual('year', ants[0].duration_type_en)
        self.assertEqual('', ants[0].prefix)
        self.assertEqual(25, ants[0].amount)
        self.assertEqual(9125, ants[0].duration_days)

    def test_complex_durations(self):
        text = 'Vier weken, 3 dagen en 151 seconden.'
        ants = list(get_duration_annotations(text=text))
        self.assertEqual(1, len(ants))
        self.assertEqual(31.0017, ants[0].duration_days)
        self.assertTrue(ants[0].is_complex)
        self.assertEqual('second', ants[0].duration_type_en)
        self.assertEqual('seconden', ants[0].duration_type)

    # def test_file_samples(self):
    #     tester = TypedAnnotationsTester()
    #     tester.test_and_raise_errors(
    #         get_ordered_durations,
    #         'lexnlp/typed_annotations/de/duration/durations.txt',
    #         DurationAnnotation)


def get_ordered_durations(text: str) -> List[DurationAnnotation]:
    ants = list(get_duration_annotations(text))
    ants.sort(key=lambda a: a.coords[0])
    return ants
