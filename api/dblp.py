import requests
import xml.etree.ElementTree as ET
import json
from collections import Counter
from models import Paper,Papers,Authors
import json_file_operations

def remove_number_in_name(name:str):
    if name[-1].isdigit() or name[-1]==' ':
        return remove_number_in_name(name[:-1])
    return name

def search_author(author_name:str):
    try:
        name_part = author_name.lower().split('_')
        url = f'https://dblp.org/search/author/api?q='
        for part in name_part:
            url += part + '$'
        firsturl = url+'&h=0&format=xml'
        response = requests.get(firsturl)

        if response.status_code != 200:
            return [],False,f'Response error: {response.status_code}'
        
        authors_xml_text = response.text
        authors_xml = ET.fromstring(authors_xml_text)

        hits_number = 0
        hits_number_info = ''
        for hits in authors_xml.iter('hits'):
            hits_number = int(hits.get('total'))
            if hits_number == 0:
                return [],False,f"No author found for name: {author_name}"
            elif hits_number >= 1 and hits_number <= 1000:
                hits_number_info = f'hit {hits.get("total")} authors for name'
            elif hits_number > 1000:
                hits_number_info = f'hit {hits.get("total")} authors for name, only first 1000 authors are shown. It is best to use more detailed names to ensure accuracy'

        secondurl = url+f'&h={hits_number}&format=xml'
        response = requests.get(secondurl)

        if response.status_code != 200:
            return [],False,f'Response error: {response.status_code}'
        
        authors_xml_text = response.text
        authors_xml = ET.fromstring(authors_xml_text)

        authors=[]

        for info in authors_xml.iter('info'):
            if info.find('author') != None and info.find('author').text.lower() == author_name.replace('_',' ').lower():
                author_url = info.find('url').text
                pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
                authors.append({'name':info.find('author').text,'dblpid':pid,'hit':'prefect'})
                continue
            elif info.find('author') != None and Counter(info.find('author').text.lower().split()) == Counter(name_part):
                author_url = info.find('url').text
                pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
                authors.append({'name':info.find('author').text,'dblpid':pid,'hit':'full'})
            else:
                author_url = info.find('url').text
                pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
                authors.append({'name':info.find('author').text,'dblpid':pid,'hit':'partial'})

        priority = {'prefect': 0, 'full': 1, 'partial': 2}
        authors.sort(key=lambda author: priority.get(author['hit'], 99))
        return authors,True,hits_number_info
    
    except requests.exceptions.RequestException as e:
        return [],False,f'Request error: {str(e)}'
    except ET.ParseError as e:
        return [],False,f'XML parsing error: {str(e)}'
    except Exception as e:
        return [],False,f'An unexpected error occurred: {str(e)}'
def find_a_paper_by_dblpid(pid:str):
    url = f'https://dblp.org/pid/{pid}.xml'
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Error:request failed, status code: {response.status_code}')
        return False
    
    author_info_xml_text = response.text
    author_info_xml = ET.fromstring(author_info_xml_text)

    if len(list(author_info_xml.iter('title'))) > 0:
        return list(author_info_xml.iter('title'))[0].text , True
    else:
        return '' , False

def fetch_author_papers(pid:str):
    url = f'https://dblp.org/pid/{pid}.xml'
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f'Error:request failed, status code: {response.status_code}')
        #print(f'Error info:\n{response.text}')
        return None
    
    author_info_xml_text = response.text
    author_info_xml = ET.fromstring(author_info_xml_text)

    papers=Papers()
    for paper_type in ['article','inproceedings']:
        for paper_xml in author_info_xml.iter(paper_type):
            paper = Paper()
            paper.type = paper_type
            for author in paper_xml.findall('author'):
                paper.author_name_list.append(remove_number_in_name(author.text))
            paper.title = paper_xml.find('title').text
            paper.year = paper_xml.find('year').text

            month = safe_find_xml_element(paper_xml,'month')
            months_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            month = months_map.get(month.lower(), '')
            paper.month = month

            paper.volume = safe_find_xml_element(paper_xml,'volume')
            paper.pages = safe_find_xml_element(paper_xml,'pages')
            paper.number = safe_find_xml_element(paper_xml,'number')
            paper.location = safe_find_xml_element(paper_xml,'journal') or safe_find_xml_element(paper_xml,'booktitle')
            for ee in paper_xml.findall('ee'):
                if ee.text.startswith('https://doi.org/'):
                    paper.doi = ee.text

            paper.tag_preprint()
            paper.cvpr_year_fix()
    return papers

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
                paper.type = 'ariticle'
            else:
                paper.type = 'inproceeding'

            paper.location = single_paper['venue']
            paper.volume = single_paper.get('volume', '')
            paper.number = single_paper.get('number', '')
            paper.pages = single_paper.get('pages', '')

            if 'https://doi.org/' in single_paper['ee']:
                paper.doi = single_paper['ee']
        except KeyError as e:
            print(single_paper)
            print(e) 
        
        paper.tag_preprint()
        papers.append(paper)
    return papers,f'Successfully fetched {len(papers.papers_list)} papers'

def safe_find_xml_element(element,subele_name):
    if element.find(subele_name) != None:
        return element.find(subele_name).text
    return ''

def test():
    result = fetch_author_papers('165/9820')
    json_file_operations.dict_to_file('papers_data.json',result.to_dict())
    #for index , single_author in enumerate(result):
    #   print(f'{index+1}. {single_author['name']} (dblp id: {single_author['dblpid']}, match type: {single_author["hit"]})')
