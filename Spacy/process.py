import spacy
import requests
from bs4 import BeautifulSoup
import numpy as np

from exceptions import NotWikiPage


npl = spacy.load('en_core_web_sm')

def _get_soup(url:str) -> BeautifulSoup:
    """Get soup object"""
    res = requests.get(url)
    return BeautifulSoup(res.content, 'html.parser')

def get_data_from_url(url:str) -> dict:
    """Returns content of all p tags found in the url"""
    if not url.startswith('https://en.wikipedia.org/wiki/'):
        raise NotWikiPage
    soup = _get_soup(url)
    para = []
    # remove '\n' from extracted data
    for p in soup.find_all('p'):
        text = p.get_text()
        text = text.replace('\n', '')
        if text:
            para.append(text)

    data = {
        'title': soup.find(id='firstHeader'),
        'para': para
    }
    return data

def get_ents_from_str(string:str) -> list[str]:
    """returns entities of verbs found in passed string"""
    doc = npl(string)
    return [f'{e.text} -> {e.label_}' for e in doc.ents]

def get_nouns_from_str(string:str) -> list[str]:
    """returns nouns of verbs found in passed string"""
    doc = npl(string)
    return [chunk.text for chunk in doc.noun_chunks]

def get_verbs_from_str(string:str) -> list[str]:
    """returns list of verbs found in passed string"""
    doc = npl(string)
    return [token.lemma_ for token in doc if token.pos_ == "VERB"]

def parse_string(string:str):
    doc = npl(string)
    result = np.array([[t.text, t.ent_type_, t.pos_] for t in doc])
    result[np.where(result=='')] = 'No Category'
    return result.tolist()
