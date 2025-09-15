import requests
import json
from models import Paper,Papers

def search_author_id(author_name:str):
    search_name=author_name.replace('_',' ')
    url = f'https://api.openalex.org/authors?search={search_name}&filter=affiliations.institution.id:I90610280'
    response = requests.get(url)
    
    if response.status_code != 200:
        return '',False,f'Error:request failed, status code: {response.status_code}'
        
    response_json = json.loads(response.text)

    if response_json['meta']['count'] == 0: 
        return '',False,f'Error:no author found for {author_name}'

    oaid = response_json['results'][0]['id'][21:]
    return oaid,True,f'Successly get {author_name}\'s OpenAlex ID: {oaid}'

def fetch_author_papers(oaid:str):

    result = []
    page = 1
    while True:
        url= f'https://api.openalex.org/works?page={page}&per-page=200&filter=authorships.institutions.lineage:i90610280,authorships.author.id:{oaid}'
        response = requests.get(url)

        if response.status_code != 200:
            return None,f'Error:request failed, status code: {response.status_code}'
        
        response_json = json.loads(response.text)
        result.extend(response_json['results'])
        if len(response_json['results']) < 200:
            break
        else:
            page += 1

    papers = Papers()

    for single_paper in result:
        paper = Paper()
        paper.type = single_paper['type']
        paper.title = single_paper['title']
        paper.year, paper.month, paper.day = single_paper['publication_date'].split('-')
        for single_author in single_paper['authorships']:
            paper.author_name_list.append(single_author['raw_author_name'])
        paper.doi = single_paper['doi'] or ''

        paper.location = ((single_paper.get('primary_location') or {}).get('source',{}) or {}).get('display_name', '')
        paper.volume = single_paper['biblio']['volume'] or ''
        paper.number = single_paper['biblio']['issue'] or ''
        if single_paper['biblio']['first_page'] and single_paper['biblio']['last_page']:
            paper.pages = (single_paper['biblio']['first_page'] + '-' + single_paper['biblio']['last_page'])
        else:
            paper.pages = single_paper['biblio']['first_page'] or single_paper['biblio']['last_page'] or ''

        paper.fwci = single_paper['fwci'] or ''

        paper.tag_preprint()
        paper.cvrp_year_fix()

        papers.append(paper)
    
    return papers
def test():
    oaid , success , message = search_author_id('Mingkui_Tan')
    print(message)

if __name__ == '__main__':
    test()