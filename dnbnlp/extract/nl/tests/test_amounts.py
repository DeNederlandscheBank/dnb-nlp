from unittest import TestCase
from num2words import num2words

from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
#from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

from dnbnlp.extract.nl.amounts import get_amounts, get_amount_annotations

def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])

class AssertionMixin(TestCase):

    def assertOneOK(self, num, writ_num):
        parsed_num = list(get_amounts(writ_num))
        self.assertEqual(len(parsed_num), 1)
        self.assertEqual(num, parsed_num[0])

    def assertSortedByLocationListEqual(self, list1, list2):
        self.assertListEqual(_sort(list1), _sort(list2))

    def assertSortedListEqual(self, list1, list2):
        self.assertListEqual(sorted(list(list1)), sorted(list(list2)))


class TestGetAmounts(AssertionMixin):
    """
    Test prepared for lexnlp method get_amounts
    """

    test_nums = (2, 15, 67, 128, 709, 1234, 3005, 16070, 735900, 900100, 999999, 1234567, 2000000)

    def assertOneOK(self, num, writ_num):
        parsed_num = list(get_amounts(writ_num))
        self.assertEqual(len(parsed_num), 1)
        self.assertEqual(num, parsed_num[0])

    def test_writ_numbers(self):
        for num in self.test_nums:
            writ_num = num2words(num, ordinal=False, lang='nl')
            self.assertOneOK(num, writ_num)

    def test_writ_numbers_ord(self):
        for num in self.test_nums:
            writ_num = num2words(num, ordinal=True, lang='nl')
            self.assertOneOK(num, writ_num)

    def test_writ_half(self):
        self.assertOneOK(6.5, 'zeseneenhalf')
        self.assertOneOK(
            2422704.5, 'tweemiljoenvierhonderdduizendtweeentwintigduizendzevenhonderdviereneenhalf')
        self.assertOneOK(500000, 'een half miljoen Dollar')
        # TODO: test 'tausendzweihundertvierunddreißig Komma fünf null'

    def test_writ_quarter(self):
        self.assertOneOK(0.75, 'driekwart')
        self.assertOneOK(1.25, 'een en een kwart')

    def test_writ_big_number(self):
        self.assertOneOK(1000, 'duizend')
        self.assertOneOK(1234, 'duizendtweehonderdvierendertig')
        self.assertOneOK(1000000, 'miljoen')

    def test_writ_mixed_number(self):
        self.assertOneOK(1000, '1 duizend')
        self.assertOneOK(5000000, '5 miljoen')

    def test_non_writ_number(self):
        self.assertOneOK(1000, 'Het is duizend dollar')
        self.assertOneOK(200000, 'Het is 200.000 euro')
        self.assertOneOK(0.5, 'Het is 0,5 vol')
        self.assertOneOK(10123.5, 'Het is 10.123,5 vol')

    def test_multiple_values_in_string(self):
        text = 'Het volume bedraagt 10 liter en kost dertig euro'
        ants = list(get_amounts(text))
        self.assertSortedListEqual(ants, [10, 30])
        text = 'Er waren 30 mensen en ze hadden in twee gevallen 2 miljoen euro'
        self.assertSortedListEqual(list(get_amounts(text)), [2, 30, 2000000])

    def test_mix_num_written(self):
        text = "1,5, driekwart, een en een kwart"
        ants = list(get_amount_annotations(text))
        self.assertEqual(2, len(ants))

    def test_wrong_cases(self):
        self.assertSortedListEqual(list(get_amounts('...%')), [])

    def test_annotations(self):
        text = 'Het volume bedraagt 10 liter en kost dertig euro'
        ants = list(get_amount_annotations(text))
        self.assertEqual(2, len(ants))
        self.assertEqual(10, ants[0].value)
        self.assertEqual((20, 23), ants[0].coords)
        self.assertEqual(30, ants[1].value)
        self.assertEqual(text.find(' dertig'), ants[1].coords[0])

    # def test_file_samples(self):
    #     tester = TypedAnnotationsTester()
    #     tester.test_and_raise_errors(
    #         get_amount_annotations,
    #         'lexnlp/typed_annotations/de/amount/amounts.txt',
    #         AmountAnnotation)
