# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from os.path import isfile, join
from os import listdir
from src.utils.text_extraction import doc2text, doc2dataframe

EXTERNAL_PATH = join('data', 'external', 'sfcr')
INTERIM_PATH = join('data', 'interim', 'sfcr')

@click.command()
@click.option('--output_path', default=EXTERNAL_PATH, help='The path of the downloaded files.')
@click.option('--interim_path', default=INTERIM_PATH, help='The path of the interim files.')

def main(output_path, interim_path):
    """Reads all pdfs in external_filepath and converts to txt and dataframes in interim_path
    """
    logger = logging.getLogger(__name__)
    logger.info('Converting pdf to txt and dataframes')

    external_files = [f for f in listdir(output_path) if isfile(join(output_path, f)) if f[-3:]=="pdf"]
    interim_files = [f for f in listdir(interim_path) if isfile(join(interim_path, f))]
    for file in external_files:
        logger.info('Processing %s' % file)
        pdf_filename = file
        txt_filename = file[:-3] + 'txt'
        pck_filename = file[:-3] + 'pickle'
        if txt_filename not in interim_files:
            convert_to_text(pdf_filename, txt_filename, output_path, interim_path)
        if pck_filename not in interim_files:
            convert_to_dataframe(pdf_filename, pck_filename, output_path, interim_path)

def convert_to_text(pdf_filename, txt_filename, output_path, interim_path):
    logger = logging.getLogger(__name__)
    logger.info('Converting %s to txt' % pdf_filename)
    logger.info('--Doc2text')
    logging.getLogger().setLevel(logging.ERROR)
    text = doc2text(join(output_path, pdf_filename))
    logging.getLogger().setLevel(logging.INFO)
    logger.info('--Saving to txt file')
    txt = open(join(interim_path, txt_filename), "wb")
    txt.write(text.encode('utf-8'))
    txt.close()

def convert_to_dataframe(pdf_filename, pck_filename, output_path, interim_path):
    logger = logging.getLogger(__name__)
    logger.info('Converting %s to dataframe' % pdf_filename)
    logger.info('--Doc2text')
    logging.getLogger().setLevel(logging.ERROR)
    df = doc2dataframe(join(output_path, pdf_filename))
    logging.getLogger().setLevel(logging.INFO)
    logger.info('--Saving to dataframe file')
    df.to_pickle(join(interim_path, pck_filename))
    
if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
