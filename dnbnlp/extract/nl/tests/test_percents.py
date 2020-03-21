from typing import List

from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
#from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

from dnbnlp.extract.nl.percents import get_percents, get_percent_annotations
from dnbnlp.extract.nl.tests.test_amounts import AssertionMixin

class TestGetPercents(AssertionMixin):
    def test_percent_prefix(self):
        text = 'je weet dat het alcoholpercentage meer dan 15 procent tot 18 procent is ... '
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 43,
                                'location_end': 54,
                                'source_text': '15 procent',
                                'unit_name': 'procent',
                                'amount': 15.0,
                                'real_amount': 15.0},
                               {'location_start': 58,
                                'location_end': 69,
                                'source_text': '18 procent',
                                'unit_name': 'procent',
                                'amount': 18.0,
                                'real_amount': 18.0}])

    def test_written_percent(self):
        text = 'Dit komt neer op twintig procent van het inkomen'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 16,
                                'location_end': 33,
                                'source_text': ' twintig procent',
                                'unit_name': 'procent',
                                'amount': 20,
                                'real_amount': 20}])
        text = 'Dit inkomen maakt twintig % van het totaalinkomen uit'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 17,
                                'location_end': 28,
                                'source_text': ' twintig %',
                                'unit_name': '%',
                                'amount': 20,
                                'real_amount': 20}])

    def test_annotations(self):
        text = 'Dit inkomen maakt twintig procent van het totaalinkomen uit'
        res = list(get_percent_annotations(text))
        self.assertEqual(1, len(
            res))
        self.assertEqual((17, 34), res[0].coords)
        self.assertEqual('twintig procent', res[0].text.strip())
        self.assertEqual('procent', res[0].sign)
        self.assertEqual(20, res[0].amount)
        self.assertEqual(20, res[0].fraction)

    # def test_file_samples(self):
    #     tester = TypedAnnotationsTester()
    #     tester.test_and_raise_errors(
    #         get_ordered_percent_annotations,
    #         'lexnlp/typed_annotations/de/percent/percents.txt',
    #         PercentAnnotation)


def get_ordered_percent_annotations(text: str) -> List[PercentAnnotation]:
    ants = list(get_percent_annotations(text))
    ants.sort(key=lambda a: a.coords[0])
    return ants
