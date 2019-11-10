# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd

from os.path import isfile, join
from os import listdir
import re
import requests
from src.nlp.text_extraction import doc2text

METADATA_PATH = join('data', 'external')
EXTERNAL_PATH = join('data', 'external', 'sfcr')
INTERIM_PATH = join('data', 'interim', 'sfcr')

@click.command()
@click.option('--output_path', default=EXTERNAL_PATH, help='The path of the downloaded files.')
@click.option('--interim_path', default=INTERIM_PATH, help='The path of the interim files.')

def main(output_path, interim_path):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Downloading SFCRs')

    df_sfcr = pd.read_csv(join(METADATA_PATH, 'metadata_sfcr.csv'))

    df_sfcr['Filename'] = ""

    def download(filename, url, output_path):
        if not(isfile(join(output_path, filename))):
            logger.info('--Retrieving %s' % filename)
            r = requests.get(url)
            f = open(join(output_path, filename),'wb+')
            f.write(r.content)
            f.close()
        else:
            logger.info('--SFCR %s already downloaded' % filename)

    for row in df_sfcr.index:
        name = df_sfcr.loc[row, 'Insurance Undertaking']
        document = df_sfcr.loc[row, 'Document Type']
        url = df_sfcr.loc[row, 'Url']
        filename = name + "_" + document + '.pdf'
        df_sfcr.loc[row, "Filename"] = filename
        download(filename, url, output_path)

    files = [f for f in listdir(interim_path) if isfile(join(interim_path, f))]    

    for row in df_sfcr.index:

        pdf_filename = df_sfcr.loc[row, "Filename"]
        txt_filename = df_sfcr.loc[row, "Filename"][:-3] + 'txt'

        if txt_filename not in files:
            logger.info('Converting %s to txt' % pdf_filename)
            logger.info('--Doc2text')
            logging.getLogger().setLevel(logging.ERROR)
            text = doc2text(join(output_path, pdf_filename))
            logging.getLogger().setLevel(logging.INFO)
            logger.info('--Saving to txt file')
            txt = open(join(interim_path, txt_filename), "wb")
            txt.write(text.encode('utf-8'))
            txt.close()
    
if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
