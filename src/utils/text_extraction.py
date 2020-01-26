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

def doc2text(path, language='en'):
    """
    Simple doc2text method.
    :param path:
    :param language:
    :return:
    """
    codec = 'utf-8'
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, codec = codec, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    text = output_string.getvalue()
    return text

def doc2dataframe(path, lang=None):
    """
    Convert pdf document to dataframe (each sentence separately)
    """

    if ("_nl_" in path.lower()) or (lang == "nl") or ("//nl//" in path.lower()):
        sentences = sentences_nl
        lang = "nl"
    else:
        sentences = sentences_en
        lang = "en"

    df = pd.DataFrame(columns = ['source', 'lang', 'page', 'sentence', 'text'])
    codec = 'utf-8'
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
                df = df.append(pd.DataFrame(columns = ['source','lang', 'page', 'sentence', 'text'], 
                                            data = [[path, lang, page_idx, sentence_idx, sentence]]), ignore_index=True)
    return df
