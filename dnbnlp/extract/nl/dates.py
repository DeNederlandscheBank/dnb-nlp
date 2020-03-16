from lexnlp.extract.common.dates import DateParser

parser = DateParser(enable_classifier_check = False, language = 'nl',
                    dateparser_settings={'PREFER_DAY_OF_MONTH': 'first',
                                         'STRICT_PARSING': False,
                                         'DATE_ORDER': 'DMY'})

get_date_annotations = parser.get_date_annotations

get_dates = parser.get_dates

get_date_list = parser.get_date_list
