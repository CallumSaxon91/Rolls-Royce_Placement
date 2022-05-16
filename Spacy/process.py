import spacy
import requests
from bs4 import BeautifulSoup


npl = spacy.load('en_core_web_sm')

def _get_soup(url:str) -> BeautifulSoup:
    res = requests.get(url)
    return BeautifulSoup(res.content, 'html.parser')

def get_data_from_url(url:str) -> dict:
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

def get_ents_from_str(string:str):
    doc = npl(string)
    return [f'{e.text} -> {e.label_}' for e in doc.ents]
