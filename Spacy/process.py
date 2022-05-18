import spacy
import requests
from bs4 import BeautifulSoup

from exceptions import NotWikiPage

# each function gets data from the text and sorts them into each catagory
npl = spacy.load('en_core_web_sm')

def _get_soup(url:str) -> BeautifulSoup:
    res = requests.get(url)
    return BeautifulSoup(res.content, 'html.parser')
 # pulls data from the url site
def get_data_from_url(url:str) -> dict:
    if not url.startswith('https://en.wikipedia.org/wiki/'):
        raise NotWikiPage
    soup = _get_soup(url)
    para = []
    # remove '\n' from extracted data
    for p in soup.find(id='bodyContent').find_all('p'):
        text = p.get_text()
        text = text.replace('\n', '')
        if text:
            para.append(text)

    data = {
        'title': soup.find(id='firstHeader'),
        'para': para
    }
    return data

# gets only entities from string 
def get_ents_from_str(string:str) -> list:
    doc = npl(string)
    return [f'{e.text} -> {e.label_}' for e in doc.ents]

# gets only nouns from string
def get_nouns_from_str(string:str) -> list:
    doc = npl(string)
    return [chunk.text for chunk in doc.noun_chunks]

# gets only verbs from string
def get_verbs_from_str(string:str) -> list:
    doc = npl(string)
    return [token.lemma_ for token in doc if token.pos_ == "VERB"]