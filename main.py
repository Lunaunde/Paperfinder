import requests
import xml.etree.ElementTree as ET
import json
import questionary
from collections import Counter
import json_file_operations
from ui.cli import run_cli
def dblp_get_author_pid(author_name):
    
    name_part = author_name.split('_')
    url = f'https://dblp.org/search/author/api?q='
    for part in name_part:
        url += part + '$'
    firsturl = url+'&h=0&format=xml'
    response = requests.get(firsturl)

    if response.status_code != 200:
        print(f'Error:response failed, status code: {response.status_code}')
        #print(f'Error info:\n{response.text}')
        return False
    
    authors_list_xml_text = response.text
    authors_list_xml = ET.fromstring(authors_list_xml_text)

    hits_number = 0
    for hits in authors_list_xml.iter('hits'):
        hits_number = int(hits.get('total'))
        if hits_number == 0:
            print(f'No author found for name: {author_name}')
            return False
        elif hits_number >= 1 and hits_number <= 1000:
            print(f'hit {hits.get("total")} authors for name')
        elif hits_number > 1000:
            print(f'hit {hits.get("total")} authors for name, only first 1000 authors are shown. It is best to use more detailed names to ensure accuracy')

    secondurl = url+f'&h={hits_number}&format=xml'
    response = requests.get(secondurl)

    if response.status_code != 200:
        print(f'Error:response failed, status code: {response.status_code}')
        #print(f'Error info:\n{response.text}')
        return False
    
    authors_list_xml_text = response.text
    authors_list_xml = ET.fromstring(authors_list_xml_text)

    authors_list=[]

    for info in authors_list_xml.iter('info'):
        if info.find('author') != None and info.find('author').text == author_name:
            author_url = info.find('url').text
            pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
            authors_list.append({'name':info.find('author').text,'dblpid':pid,'hit':'prefect'})
            continue
        elif info.find('author') != None and Counter(info.find('author').text.split()) == Counter(name_part):
            author_url = info.find('url').text
            pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
            authors_list.append({'name':info.find('author').text,'dblpid':pid,'hit':'full'})
        else:
            author_url = info.find('url').text
            pid = author_url.split('/')[-2]+'/'+author_url.split('/')[-1]
            authors_list.append({'name':info.find('author').text,'dblpid':pid,'hit':'partial'})

    priority = {'prefect': 0, 'full': 1, 'partial': 2}
    authors_list.sort(key=lambda author: priority.get(author['hit'], 99))

    print(f'prefect hit and full hit:')

    for index,single_author in enumerate(authors_list):
        if single_author.get('hit') == None or single_author['hit'] == 'partial' :
            break
        print(f'{index+1}. {single_author["name"]} (dblp id: {single_author["dblpid"]}, match type: {single_author["hit"]})')
    
    command = input('you can use command behide:\n'
        'moreinfo show more')

    return

def load_xml_optional_subele(target_dict,element,subele_name):
    if element.find(subele_name) != None:
        target_dict[subele_name] = element.find(subele_name).text
    return
def dblp_fetch_author_papers(index):
    pid=authors_papers_data['authorlist'][index]['dblpid']
    url = f'https://dblp.org/pid/{pid}.xml'
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f'Error:request failed, status code: {response.status_code}')
        #print(f'Error info:\n{response.text}')
        return False
    
    author_info_xml_text = response.text
    author_info_xml = ET.fromstring(author_info_xml_text)

    papers_list = []
    for paper_type in ['article','inproceedings']:
        for paper_xml in author_info_xml.iter(paper_type):
            paper_data = {
                'authors':[]
                ,'ee':[]
            }
            paper_data['type'] = paper_type
            for author in paper_xml.findall('author'):
                paper_data['authors'].append(author.text)
            paper_data['title'] = paper_xml.find('title').text
            paper_data['year'] = paper_xml.find('year').text
            load_xml_optional_subele(paper_data,paper_xml,'month')
            load_xml_optional_subele(paper_data,paper_xml,'volume')
            load_xml_optional_subele(paper_data,paper_xml,'pages')
            load_xml_optional_subele(paper_data,paper_xml,'number')
            load_xml_optional_subele(paper_data,paper_xml,'journal')
            load_xml_optional_subele(paper_data,paper_xml,'booktitle')
            for ee in paper_xml.findall('ee'):
                paper_data['ee'].append(ee.text)
            papers_list.append(paper_data)
    #print(json.dumps(paper_data, indent=4))
    return papers_list
def papers_data_merge(existing_papers, new_papers):
    for new_paper in new_papers:
        match_status = 'new'
        for existing_paper in existing_papers:
            if new_paper.get('title') == existing_paper.get('title'):

                match_status = 'same title'

                for ee in new_paper.get('ee', []):
                    if ee in existing_paper.get('ee', []):
                        match_status = 'exist'
                        break
                if match_status == 'exist':
                    merged_ee = list(set(existing_paper.get('ee', []) + new_paper.get('ee', [])))
                    existing_paper.update(new_paper)
                    existing_paper['ee'] = merged_ee
                    break

                if (new_paper.get('journal') == existing_paper.get('journal')):
                    match_status = 'same journal'
                if (new_paper.get('booktitle') == existing_paper.get('booktitle')):
                    match_status = 'same booktitle'
                if (match_status == 'same journal' or match_status == 'same booktitle'):
                    if(new_paper.get('volume') == existing_paper.get('volume') or
                       new_paper.get('pages') == existing_paper.get('pages') or
                       new_paper.get('number') == existing_paper.get('number')):
                        match_status = 'NMC_SDM' # need manual check, suspiciously different metadata
                    else:
                        match_status = 'NMC_UR' # need manual check, unknown relation
                elif new_paper.get('year') == existing_paper.get('year'):
                    match_status = 'NMC_SY_DJ/B' # need manual check, same year, different journal/booktitle
                else:
                    match_status = 'different'
        if match_status == 'exist':
            continue
        else:
            if match_status == 'NMC_SDM':
                new_paper['need_manual_check'] = 'suspiciously different metadata'
            elif match_status == 'NMC_UR':
                new_paper['need_manual_check'] = 'unknown relation'
            elif match_status == 'NMC_SY_DJ/B':
                new_paper['need_manual_check'] = 'same year, different journal/booktitle'
            existing_papers.append(new_paper) # include 'new' and 'different' match_status

    existing_papers.sort(key = lambda paper:[paper['year'],paper.get('month')], reverse=True)

    return existing_papers
                
def main():
    global author_list
    data_dict=json_file_operations.file_to_dict('authors_papers_data.json')
    # authors_papers_data, is_jsonfile_load = jsonfile_to_dict('authors_papers_data.json')
    # if is_jsonfile_load == False:
    #     authors_papers_data['authorlist'] = []
    # running = True
    # print('Welcome to the PaperFinder! Use "help" command to see available commands.')
    # while running:
    #     command = input()
    #     running = command_processing(command)
        
    # dict_to_jsonfile('authors_papers_data.json',authors_papers_data)
    # return

if __name__ == '__main__':
    main()
