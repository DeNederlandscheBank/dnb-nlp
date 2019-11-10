# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import re

art_dict= dict({
                'BG': ['Член',      'pre'],
                'CS': ['Článek',    'pre'],
                'DA': ['Artikel',   'pre'],
                'DE': ['Artikel',   'pre', 'TITEL|KAPITEL|ABSCHNITT|Unterabschnitt'],
                'EL': ['Άρθρο',     'pre'],
                'EN': ['Article',   'pre', 'TITLE|CHAPTER|SECTION|Subsection'],
                'ES': ['Artículo',  'pre'],
                'ET': ['Artikkel',  'pre'],
                'FI': ['artikla',   'post'],
                'FR': ['Article',   'pre', 'TITRE|CHAPITRE|SECTION|Sous-section'],
                'HR': ['Članak',    'pre'],
                'HU': ['cikk',      'postdot'],
                'IT': ['Articolo',  'pre'],
                'LT': ['straipsnis','post'],
                'LV': ['pants',     'postdot'],
                'MT': ['Artikolu',  'pre'],
                'NL': ['Artikel',   'pre', 'TITEL|HOOFDSTUK|AFDELING|Onderafdeling'],
                'PL': ['Artykuł',   'pre'],
                'PT': ['Artigo',    'pre'],
                'RO': ['Articolul', 'pre'],
                'SK': ['Článok',    'pre'],
                'SL': ['Člen',      'pre'],
                'SV': ['Artikel',   'pre']})

def article_regex(language, num):
    order = art_dict[language][1]
    headings = art_dict[language][2]
    art_id = art_dict[language][0]
    if order == 'pre':
        string = art_id+'\s('+str(num)+')\s\n\n(.*?)(\n\n.*?)\n((\s'+headings+').*)?'+art_id+'\s'+str(num+1)
    elif order == 'post':
        string = str(num)+'\s('+art_id+')\s(.*?)'+str(num+1)+' '+art_id
    elif order == 'postdot':
        string = str(num)+'.\s('+art_id+')\s(.*?)'+str(num+1)+'. '+art_id
    return re.compile(string, re.DOTALL)

def retrieve_article(text, language, num):
    art_re = article_regex(language, num)
    art_text = art_re.search(text)
    art_num = int(art_text[1])
    art_title = ' '.join(art_text[2].split())
    art_body = art_text[3]
    if art_body[0:4] == '\n\n1.': 
        # if the article start with '1.' then it has numbered paragraphs
        paragraph_re = re.compile('\n\n(\d+)\.\n(.*?)(?=(\n\n(\d+)\.\n)|$)', re.DOTALL)
        art_paragraphs = [(int(p[0]), p[1]) for p in paragraph_re.findall(art_body)]
    else:
        art_paragraphs = [(0, ' '.join(art_body.split()))]
    return (art_num, art_title, art_paragraphs)