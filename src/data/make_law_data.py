# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from os.path import isfile, join
from os import listdir
import re
import requests
from src.nlp.text_extraction import doc2text

EXTERNAL_PATH = join('data', 'external', 'law')
INTERIM_PATH = join('data', 'interim', 'law')

@click.command()
@click.option('--language', prompt = "Language to download (BG,ES,CS,DA,DE,ET,EL,EN,FR,HR,IT,LV,LT,HU,MT,NL,PL,PT,RO,SK,SL,FI,SV or ALL)", default=None, help='The language of the legislation you want to download.')
@click.option('--output_path', default=EXTERNAL_PATH, help='The path of the downloaded files.')
@click.option('--interim_path', default=INTERIM_PATH, help='The path of the interim files.')

def main(language_id, output_path, interim_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Downloading laws')

    EU_languages = ['BG','ES','CS','DA','DE','ET','EL','EN','FR','HR','IT','LV','LT','HU',
                    'MT','NL','PL','PT','RO','SK','SL','FI','SV']

    urls = {lang: 'https://eur-lex.europa.eu/legal-content/' + lang +
            '/TXT/PDF/?uri=OJ:L:2015:012:FULL&from=EN' for lang in EU_languages}

    def download(language_id, url, output_path):
        filename = 'Solvency II Delegated Acts - ' + language_id + '.pdf'
        if not(isfile(join(output_path, filename))):
            logger.info('Retrieving %s' % language_id)
            r = requests.get(url)
            f = open(join(output_path, filename),'wb+')
            f.write(r.content)
            f.close()
        else:
            logger.info('Language %s already downloaded' % language_id)

    if language_id != "ALL":
        if language_id in EU_languages:
            languages = [language_id]
        else:
            logger.info('Unknown language specified: %s' % language_id)
            languages = []
    else:
        languages = EU_languages

    for language in languages:
        download(language, urls[language], output_path)

    DA_dict = dict({
                    'BG': 'Официален вестник на Европейския съюз',
                    'CS': 'Úřední věstník Evropské unie',
                    'DA': 'Den Europæiske Unions Tidende',
                    'DE': 'Amtsblatt der Europäischen Union',
                    'EL': 'Επίσημη Εφημερίδα της Ευρωπαϊκής Ένωσης',
                    'EN': 'Official Journal of the European Union',
                    'ES': 'Diario Oficial de la Unión Europea',
                    'ET': 'Euroopa Liidu Teataja',           
                    'FI': 'Euroopan unionin virallinen lehti',
                    'FR': "Journal officiel de l'Union européenne",
                    'HR': 'Službeni list Europske unije',         
                    'HU': 'Az Európai Unió Hivatalos Lapja',      
                    'IT': "Gazzetta ufficiale dell'Unione europea",
                    'LT': 'Europos Sąjungos oficialusis leidinys',
                    'LV': 'Eiropas Savienības Oficiālais Vēstnesis',
                    'MT': 'Il-Ġurnal Uffiċjali tal-Unjoni Ewropea',
                    'NL': 'Publicatieblad van de Europese Unie',  
                    'PL': 'Dziennik Urzędowy Unii Europejskiej',  
                    'PT': 'Jornal Oficial da União Europeia',     
                    'RO': 'Jurnalul Oficial al Uniunii Europene', 
                    'SK': 'Úradný vestník Európskej únie',        
                    'SL': 'Uradni list Evropske unije',            
                    'SV': 'Europeiska unionens officiella tidning'})

    files = [f for f in listdir(interim_path) if isfile(join(interim_path, f))]    

    for language in languages:
        if not("Delegated_Acts_" + language + ".txt" in files):
            
            logger.info('Converting %s to txt (this may take a while)' % language)
            
            # reading pages from pdf file
            logger.info('--Doc2text')
            logging.getLogger().setLevel(logging.ERROR)
            da_text = doc2text(join(output_path, 'Solvency II Delegated Acts - ' + language + '.pdf'))
            logging.getLogger().setLevel(logging.INFO)

            # deleting page headers
            logger.info('--Deleting page headers')
            #         "17.1.2015\n\nEN     \n\nOfficial Journal of  the European Union \n\nL 12/5"
            header1 = "\\s+17.1.2015\\s+"+language+"\\s+" + DA_dict[language].replace(' ','\\s+') + "\\s+L\\s+\\d+\\/\\d+\\s"
            #         "L 12/56 \n\nEN     \n\nOfficial Journal of  the European Union \n\n17.1.2015"
            header2 = "L\\s+\\d+\\/\\d+\\s+" + language + "\\s+" + DA_dict[language].replace(' ','\\s+') + "\\s+17.1.2015\\s+"
            da_text = re.sub(header1, '', da_text)
            da_text = re.sub(header2, '', da_text)
    
            # some preliminary cleaning -> should be more 
            da_text = da_text.replace('\xad ', '')
   
            # saving txt file
            logger.info('--Saving to txt file')
            da_txt = open(join(interim_path, "Delegated_Acts_" + language + ".txt"), "wb")
            da_txt.write(da_text.encode('utf-8'))
            da_txt.close()
        else:
            logger.info('Language %s already converted to txt file' % language)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
