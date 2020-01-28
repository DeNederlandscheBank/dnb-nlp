# -*- coding: utf-8 -*-

from io import StringIO
import pandas as pd
import logging

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from lexnlp.nlp.en.segments import sentences as sentences_en
from src.nlp.nl.segments import sentences as sentences_nl

import nltk
from bs4 import BeautifulSoup

def doc2text(path, language='en'):
    """
    Simple doc2text method.
    :param path:
    :param language:
    :return:
    """
    codec = 'utf-8'
    output_string = StringIO()
    if path[-3:].lower()=='pdf':
        with open(path, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, codec = codec, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
        text = output_string.getvalue()
    elif path[-4:].lower()=='html':
        with open(path, 'rb') as in_file:
            soup = BeautifulSoup(in_file)
            text = soup.get_text()
    return text

def doc2dataframe(path, language=None, document_type=None, document_year=None):
    """
    Convert pdf document to dataframe (each sentence separately)
    """
    if language is not None:
        if ("_nl_" in path.lower()) or (language == "nl") or ("//nl//" in path.lower()):
            sentences = sentences_nl
            language = "nl"
        else:
            sentences = sentences_en
            language = "en"

    df = pd.DataFrame(columns = ['source', 'language', 'document type', 'document year', 'page', 'sentence', 'text'])
    codec = 'utf-8'
    if path[-3:].lower()=='pdf':
        with open(path, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            for page_idx, page in enumerate(PDFPage.create_pages(doc)):
                output_string = StringIO()
                rsrcmgr = PDFResourceManager()
                device = TextConverter(rsrcmgr, output_string, codec = codec, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                text = output_string.getvalue()
                text = sentences.pre_process_document(text)
                for sentence_idx, sentence in enumerate(sentences.get_sentence_list(text)):
                    df = df.append(pd.DataFrame(columns = ['source','language', 'document type', 'document year', 'page', 'sentence', 'text'], 
                                                data = [[path, language, document_type, document_year, page_idx, sentence_idx, sentence]]), ignore_index=True)
    elif path[-4:].lower()=='html':
        with open(path, 'rb') as in_file:
            soup = BeautifulSoup(in_file)
            text = soup.get_text()
            text = sentences.pre_process_document(text)
            for sentence_idx, sentence in enumerate(sentences.get_sentence_list(text)):
                    df = df.append(pd.DataFrame(columns = ['source','language', 'document type', 'document year', 'page', 'sentence', 'text'], 
                                                data = [[path, language, document_type, document_year, 0, sentence_idx, sentence]]), ignore_index=True)

    return df
