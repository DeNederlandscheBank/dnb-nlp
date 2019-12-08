#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Unit tests for Dates.
"""

import datetime
from unittest import TestCase

from typing import List

from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
#from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

from src.extract.nl.dates import get_date_list, get_date_annotations

class TestNlDatesPlain(TestCase):

    def test_dates(self):
        text = """
        Verschijningsdatum: 23-05-1975, \
        "Vanaf 29 maart 2017 gaan we het anders doen" \
        verschenen op 29/3/2018""".strip()

        ds = get_date_list(text=text, language='nl')
        self.assertEqual(3, len(ds))
        ds.sort(key=lambda d:d['location_start'])

        self.assertEqual((20, 30), (ds[0]['location_start'], ds[0]['location_end']))
        self.assertEqual((47, 60), (ds[1]['location_start'], ds[1]['location_end']))
        self.assertEqual((108, 117), (ds[2]['location_start'], ds[2]['location_end']))

        self.assertEqual(datetime.datetime(1975, 5, 23, 0, 0), ds[0]['value'])
        self.assertEqual(datetime.datetime(2017, 3, 29, 0, 0), ds[1]['value'])
        self.assertEqual(datetime.datetime(2018, 3, 29, 0, 0), ds[2]['value'])

        self.assertEqual('23-05-1975', ds[0]['source'])
        self.assertEqual('29 maart 2017', ds[1]['source'])
        self.assertEqual('29/3/2018', ds[2]['source'])

def get_dates_ordered(text: str) -> List[DateAnnotation]:
    dates = list(get_date_annotations(text))
    dates.sort(key=lambda d: d.coords[0])
    return dates
