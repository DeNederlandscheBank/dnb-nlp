# -*- coding: utf-8 -*-

from io import StringIO
import pandas as pd
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from lexnlp.nlp.en.segments import sentences

def doc2text(path, language='eng'):
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

def doc2dataframe(path, language='eng'):
    """
    Convert pdf document to dataframe (each sentence separately)
    """
    df = pd.DataFrame(columns = ['source', 'page', 'sentence', 'text'])
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
            for sentence_idx, sentence in enumerate(sentences.get_sentence_list(text)):
               df = df.append(pd.DataFrame(columns = ['source','page', 'sentence', 'text'], 
                                           data = [[path, page_idx, sentence_idx, sentence]]), ignore_index=True)
    return df
