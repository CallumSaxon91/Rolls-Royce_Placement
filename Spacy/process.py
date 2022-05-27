import spacy  # takes a long time
import requests
import logging
import numpy as np
from bs4 import BeautifulSoup
from io import TextIOWrapper

from exceptions import NotWikiPage


log = logging.getLogger(__name__)
npl = spacy.load('en_core_web_sm')  # also takes a long time

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
        'title': soup.find(id='firstHeading').contents[0],
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
    result[np.where(result=='')] = 'N/A'
    return result.tolist()

def parse_from_file(file:TextIOWrapper):
    content = file.readlines()
    if any((line.startswith('https://') for line in content)):
        data = get_data_from_url(content[0])  # only gets first url TODO: complete this
        return parse_string(data['content'])
    else:
        return parse_string(''.join(content))

def group_entities(data:list[list, list]) -> list[list, list]:
    grouped_data = []
    last_ent = ''
    group = ''
    for row in data:
        word = row[0]
        ent = row[1]
        pos = row[2]
        if ent == last_ent:
            group += f'{word} '
        else:
            grouped_data.append([group, last_ent, 'SENTENCE' if ' ' in group else pos])
            group = ''
        last_ent = ent
    return grouped_data

# def get_linked_data():
#     response = requests.get(
#         f'http://api.conceptnet.io/query?start=/c/en/apple&rel=/r/ExternalURL&limit=1000'
#     )
#     obj = response.json()
#     print(obj)
#     return [edge['end']['@id'] for edge in obj['edges']]

# print(get_linked_data())
