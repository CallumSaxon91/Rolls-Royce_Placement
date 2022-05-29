import logging

from exceptions import NotWikiPage


log = logging.getLogger(__name__)

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
