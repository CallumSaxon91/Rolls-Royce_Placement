import spacy
import requests
import logging
import numpy as np
from bs4 import BeautifulSoup

from exceptions import NotWikiPage


log = logging.getLogger(__name__)
npl = spacy.load('en_core_web_sm')

def _get_soup(url:str) -> BeautifulSoup:
    """Get soup object"""
    res = requests.get(url)
    return BeautifulSoup(res.content, 'html.parser')

def get_data_from_url(url:str, searchfor:str='p') -> dict:
    """Returns content of all p tags found in the url"""
    if not url.startswith('https://en.wikipedia.org/wiki/'):
        raise NotWikiPage
    soup = _get_soup(url)
    content = []
    # remove '\n' from extracted data
    for p in soup.find_all(searchfor):
        text = p.get_text()
        text = text.replace('\n', '')
        if text:
            content.append(text)

    data = {
        'title': soup.find(id='firstHeader'),
        'content': content
    }
    return data

def parse_pos_from_string(string:str, pos:str):
    """parse only matching pos"""
    doc = npl(string)
    return [[t.text, t.pos_] for t in doc if t.pos_ == pos]

def parse_string(string:str):
    """
        parse a string of characters into a 2d array of text, entity
        type and pos.
    """
    doc = npl(string)
    result = np.array([[t.text, t.ent_type_, t.pos_] for t in doc])
    result[np.where(result=='')] = 'No Category'
    return result.tolist()
