# -*- coding: utf-8 -*-

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
 
from os.path import isfile, join, exists
from os import listdir, walk, makedirs
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
    logger.info('Reading in %s' % output_path)
    logger.info('Writing in %s' % interim_path)
    external_files = []
    for dirpath, dirnames, filenames in walk(output_path):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            external_files.append((dirpath, filename))
 
    for file in external_files:
        logger.info('Processing %s' % file[1])
        pdf_filename = file[1]
        txt_filename = file[1][:-3] + 'txt'
        pck_filename = file[1][:-3] + 'pickle'
        new_dir = join(interim_path, file[0][len(output_path):])
        if not exists(new_dir):
            makedirs(new_dir)
        if not isfile(join(new_dir, txt_filename)):
            convert_to_text(pdf_filename, txt_filename, file[0], new_dir)
        if not isfile(join(new_dir, pck_filename)):
            convert_to_dataframe(pdf_filename, pck_filename, file[0], new_dir)
 
def convert_to_text(pdf_filename, txt_filename, output_path, interim_path):
    logger = logging.getLogger(__name__)
    logger.info('Converting %s to txt' % pdf_filename)
    logger.info('--Doc2text')
    logging.getLogger().setLevel(logging.ERROR)
    text = doc2text(join(output_path, pdf_filename))
    logging.getLogger().setLevel(logging.INFO)
    logger.info('--Saving to txt file')
    txt = open(join(interim_path, txt_filename), "wb")
    logger.info('--Writing file %s' % str(join(interim_path, txt_filename)))
    txt.write(text.encode('utf-8'))
    txt.close()
 
def convert_to_dataframe(pdf_filename, pck_filename, output_path, interim_path):
    logger = logging.getLogger(__name__)
    logger.info('Converting %s to dataframe' % pdf_filename)
    logger.info('--Doc2DataFrame')
    logging.getLogger().setLevel(logging.ERROR)
    df = doc2dataframe(join(output_path, pdf_filename))
    logging.getLogger().setLevel(logging.INFO)
    logger.info('--Saving to dataframe file')
    logger.info('--Writing file %s' % str(join(interim_path, txt_filename)))
    df.to_pickle(join(interim_path, pck_filename))
   
if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
