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
from src.utils.text_extraction import doc2text, doc2dataframe

from bs4 import BeautifulSoup as soup
import urllib

METADATA_PATH = join('data', 'external')
EXTERNAL_PATH = join('data', 'external', 'sfcr')
INTERIM_PATH = join('data', 'interim', 'sfcr')

@click.command()
@click.option('--output_path', default=EXTERNAL_PATH, help='The path of the downloaded files.')
@click.option('--interim_path', default=INTERIM_PATH, help='The path of the interim files.')

def main(output_path, interim_path):
    """Downloads pdfs from internet in external_path 
       based on contents in metadata_sfcr.csv and 
       converts to txt and dataframes in interim_path
    """
    logger = logging.getLogger(__name__)
    logger.info('Downloading SFCRs')

    df_sfcr = pd.read_csv(join(METADATA_PATH, 'metadata_sfcr.csv'), encoding = 'Latin-1')
    df_sfcr['Filename'] = ""
    df_sfcr['Number of pdfs'] = 0

    for row in df_sfcr.index:
        name = df_sfcr.loc[row, 'Insurance Undertaking']
        document = df_sfcr.loc[row, 'Document Type']
        url = df_sfcr.loc[row, 'Url']
        lang = df_sfcr.loc[row, 'Language']
        url_type = df_sfcr.loc[row, 'Url Type']
        year = df_sfcr.loc[row, 'Year']
        filename = str(year) + "_" + str(lang) + "_" + name + "_" + document + '.pdf'
        df_sfcr.loc[row, "Filename"] = filename
        if url_type=="PDF":
            n_pdfs = download_pdf(filename, url, output_path)
        else:
            n_pdfs = download_html(filename, url, output_path)
        df_sfcr.loc[row, "Number of pdfs"] = n_pdfs

    files = [f for f in listdir(interim_path) if isfile(join(interim_path, f))]    
    for row in df_sfcr.index:
        if df_sfcr.loc[row, "Url Type"]=="PDF":
            pdf_filename = df_sfcr.loc[row, "Filename"]
            txt_filename = df_sfcr.loc[row, "Filename"][:-3] + 'txt'
            pck_filename = df_sfcr.loc[row, "Filename"][:-3] + 'pickle'
            if txt_filename not in files:
                convert_to_text(pdf_filename, txt_filename, output_path, interim_path)
            if pck_filename not in files:
                convert_to_dataframe(pdf_filename, pck_filename, output_path, interim_path)
        else:
            for n in range(df_sfcr.loc[row, "Number of pdfs"]):
                pdf_filename = df_sfcr.loc[row, "Filename"][:-4] + "_"+str(n+1) + ".pdf"
                txt_filename = pdf_filename[:-3]+'txt'
                pck_filename = df_sfcr.loc[row, "Filename"][:-4] + "_"+str(n+1) + ".pickle"
                if txt_filename not in files:
                    convert_to_text(pdf_filename, txt_filename, output_path, interim_path)
                if pck_filename not in files:
                    convert_to_dataframe(pdf_filename, pck_filename, output_path, interim_path)

def download_pdf(filename, url, output_path):
    logger = logging.getLogger(__name__)
    if not(isfile(join(output_path, filename))):
        logger.info('--Retrieving %s' % filename)
        r = requests.get(url)
        f = open(join(output_path, filename),'wb+')
        f.write(r.content)
        f.close()
    else:
        logger.info('--SFCR %s already downloaded' % filename)
    return 0

def download_html(filename, url, output_path):
    logger = logging.getLogger(__name__)
    html = requests.get(url)
    if html.status_code==200:
        bs = soup(html.text, features="html.parser")
        links = bs.findAll('a')
        n_pdfs = 0
        for link in links:
            link_string = str(link).lower()
            if (("sfcr" in link_string) or 
                ("solvency and financial condition" in link_string) or
                ("solvency financial condition" in link_string)) and (".pdf" in link_string):
                content = requests.get(urllib.parse.urljoin(url, link['href']), output_path)
                if content.status_code==200 and content.headers['content-type']=='application/pdf':
                    n_pdfs += 1
                    f = filename[:-4]+"_"+str(n_pdfs)+'.pdf'
                    if not(isfile(join(output_path, f))):
                        with open(join(output_path, f), 'wb') as pdf:
                            pdf.write(content.content)
                            logger.info('--Retrieving %s' % f)
                    else:
                        logger.info('--SFCR %s already downloaded' % f)
    return n_pdfs

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

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
