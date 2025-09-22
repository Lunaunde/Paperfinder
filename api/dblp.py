import requests
import json
from collections import Counter
from models import Paper,Papers,Authors

def remove_number_in_name(name:str):
    if name[-1].isdigit() or name[-1]==' ':
        return remove_number_in_name(name[:-1])
    return name

def fetch_author_papers_by_name(author_name:str):
    result = []
    name = author_name.replace('_',' ')
    url_head = f'https://dblp.org/search/publ/api?q={name}&format=json&h=1000'
    f = 0
    while True:
        url = url_head + f'&f={f}'
        response = requests.get(url)
        if response.status_code != 200:
            return None,f'Error:request failed, status code: {response.status_code}'
        response_json = json.loads(response.text)
        if 'hit' in response_json['result']['hits']:
            result.extend(response_json['result']['hits']['hit'])

        if(int(response_json['result']['hits']['@total']) < (f+1)*1000 ):
            break
        else:
            f += 1000
    
    papers = Papers()

    for single_hit in result:
        paper = Paper()
        single_paper = single_hit['info']
        try:
            paper.title = single_paper['title']
            paper.year = single_paper['year']

            if single_paper['key'].split('/')[0] == 'journal':
                paper.type = 'article'
            elif single_paper['key'].split('/')[0] == 'conf':
                paper.type = 'inproceedings'
            else:
                paper.type = single_paper['key'].split('/')[0]

            try:
                if isinstance(single_paper['authors']['author'], list):
                    for single_author in single_paper['authors']['author']:
                        paper.author_name_list.append(remove_number_in_name(single_author['text']))
                else:
                    paper.author_name_list.append(remove_number_in_name(single_paper['authors']['author']['text']))
            except TypeError as e:
                print(single_paper)
                print(e)

            paper.source = single_paper.get('venue', '')
            paper.volume = single_paper.get('volume', '')
            paper.number = single_paper.get('number', '')
            paper.pages = single_paper.get('pages', '')

            if 'ee' in single_paper and 'https://doi.org/' in single_paper['ee']:
                paper.doi = single_paper['ee']
        except KeyError as e:
            print(single_paper)
            print(e) 
        
        paper.tag_preprint()
        papers.append(paper)
    return papers,f'Successfully fetched {len(papers.papers_list)} papers'
