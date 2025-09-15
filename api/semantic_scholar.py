import requests
import json
from models import Author,Papers,Paper
def search_s2id(title):
    # if len(author.papers.papers_list) < 1:
    #     return '',False,'Searching S2ID need at least one paper'
    # paper = author.papers.papers_list[0]
    # url = f'https://api.semanticscholar.org/graph/v1/paper/search/match?query={paper.title}'
    url = f'https://api.semanticscholar.org/graph/v1/paper/search?query={title}'
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Error:request failed, status code: {response.status_code}')
        return '',False,f'Error:request failed, status code: {response.status_code}'
    
    print (response.text)

def test():
    search_s2id('Construction of the Literature Graph in Semantic Scholar')