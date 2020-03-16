from typing import List
import pandas as pd
import io

from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
#from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

from src.extract.nl.geoentities import get_geoentity_list, get_geoentity_annotations
from src.extract.nl.tests.test_amounts import AssertionMixin

sample_csv = '''
"Entity ID","Entity Category","Entity Name","Entity Priority","Dutch Name","Spanish Name","French Name","ISO-3166-2","ISO-3166-3","Alias","Latitude","Longitude"
1,"Countries","Afghanistan",800,"Afghanistan","Afganistán;República Islámica de Afganistán","l'Afghanistan","AF","AFG","","33","66"
2,"Countries","Albania",800,"Albanië","República de Albania;Albania","l'Albanie;la République d'Albanie","AL","ALB","","41","20"
3,"Countries","Algeria",800,"Algerije","República Argelina Democrática y Popular;Argelia","Algérie","DZ","DZA","","28","3"
83,"Countries","Georgia",800,"Georgië","República de Georgia;Georgia","la Géorgie","GE","GEO","","41.99998","43.4999"
999,"Dummy","Georgia",700,"Georgië","República de Georgia;Georgia","la Géorgie","GE","GEO","","41.99998","43.4999"
'''
file_like = io.StringIO(sample_csv)
entity_df = pd.read_csv(file_like)

class TestGetGeoEntities(AssertionMixin):
    default_columns = ["Entity ID",
                       "Entity Category",
                       "Entity Name",
                       "Entity Priority",
                       "Dutch Name",
                       "ISO-3166-2",
                       "ISO-3166-3",
                       "Alias"]

    def test_extract_geo(self):
        text = """some odd text and Georgië mentioned inside it"""
        res = get_geoentity_list(text,
                                 entity_df,
                                 parse_columns=["Dutch Name", "ISO-3166-2", "ISO-3166-3", "Alias"],
                                 result_columns={i: i for i in self.default_columns},
                                 preformed_entity={'Entity Type': 'geo entity'},
                                 priority_sort_column="Entity Priority")
        self.assertEqual(res, [{'location_start': 17,
                                'location_end': 26,
                                'source': 'Georgië',
                                'Entity ID': 999,
                                'Entity Category': 'Dummy',
                                'Entity Name': 'Georgia',
                                'Entity Priority': 700,
                                'Dutch Name': 'Georgië',
                                'ISO-3166-2': 'GE',
                                'ISO-3166-3': 'GEO',
                                'Alias': '',
                                'Entity Type': 'geo entity'}])

        res = get_geoentity_list(text, entity_df,
                                 parse_columns=["Dutch Name", "ISO-3166-2", "ISO-3166-3", "Alias"],
                                 result_columns={i: i for i in self.default_columns[:-1]},
                                 preformed_entity={'Entity Type': 'SOME TAG'},
                                 priority_sort_column="Entity Priority",
                                 priority_sort_ascending=False)
        self.assertEqual(res, [{'location_start': 17,
                                'location_end': 26,
                                'source': 'Georgië',
                                'Entity ID': 83,
                                'Entity Category': 'Countries',
                                'Entity Name': 'Georgia',
                                'Entity Priority': 800,
                                'Dutch Name': 'Georgië',
                                'ISO-3166-2': 'GE',
                                'ISO-3166-3': 'GEO',
                                'Entity Type': 'SOME TAG'}])

    def test_nl_annotations(self):
        text = "some odd text and Georgië mentioned inside it"
        ants = list(get_geoentity_annotations(
                   text,
                   entity_df,
                   preformed_entity={'Entity Type': 'geo entity'},
                   priority_sort_column="Entity Priority"))
        self.assertEqual(1, len(ants))
        self.assertEqual((17, 26), ants[0].coords)

        self.assertEqual(999, ants[0].entity_id)
        self.assertEqual('Dummy', ants[0].entity_category)
        self.assertEqual('Georgië', ants[0].source)
        self.assertEqual('Georgië', ants[0].name)
        self.assertEqual('Georgia', ants[0].name_en)
        self.assertEqual(700, ants[0].entity_priority)
        self.assertEqual('GE', ants[0].iso_3166_2)
        self.assertEqual('GEO', ants[0].iso_3166_3)
        self.assertEqual('', ants[0].alias)

    # def test_file_samples(self):
    #     tester = TypedAnnotationsTester()
    #     tester.test_and_raise_errors(
    #         get_ordered_geo_annotations,
    #         'lexnlp/typed_annotations/de/geoentity/geoentities.txt',
    #         GeoAnnotation)


def get_ordered_geo_annotations(text: str) -> List[GeoAnnotation]:
    ants = list(get_geoentity_annotations(text, entity_df))
    ants.sort(key=lambda a: a.coords[0])
    return ants
