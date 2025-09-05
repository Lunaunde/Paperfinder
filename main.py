import requests
import xml.etree.ElementTree as ET
import json
import questionary
from collections import Counter

def jsonfile_to_dict(filename):
    try:
        with open(filename,'r',encoding='utf-8') as file:
            data_dict = json.load(file)
        print(f'Loaded {filename} successfully')
        return data_dict, True
    except FileNotFoundError:
        print(f"Error:file {filename} not found")
    except json.JSONDecodeError as errorinfo:
        print(f'Error:failed to decode JSON from file {filename}, error info:\n{errorinfo}')
    except Exception as errorinfo:
        print(f'Error:an unexpected error occurred while reading file {filename}, error info:\n{errorinfo}')
    return {}, False

def dict_to_jsonfile(filename,data_dict):
    try:
        with open(filename,'w',encoding='utf-8') as file:
            json.dump(data_dict,file,indent=4)
        print(f'Saved {filename} successfully')
        return True
    except Exception as errorinfo:
        print(f'Error:an unexpected error occurred while writing file {filename}, error info:\n{errorinfo}')
        return False

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

def command_processing(command):
    if command.split()[0] == 'help':
        print(
        '0. exit - exit program\n'
        '1. author\n'
        'author list - show mainly info of all authors in list\n'
        'author add <name> <displayName>(optional) - add a new author to authorlist, use "_" to replace space in name\n'
        'author get <name/displayName> - get author info by name\n'
        'author modify <name/displayName> [displayName/dblpid] [auto/set] <value> - modify author info by name.\n'
        'author remove <name> - remove an author from authorlist by name\n'
        )
    elif command.split()[0] == 'author':
        if len(command.split()) < 2:
            print('Useage: author <list/add/info/modify/remove> ... Or use "help" command to see available commands')
        elif command.split()[1] == 'list':
            if len(authors_papers_data['authorlist']) == 0:
                print('No author in authorlist, use "author add ..." to add a new author')
            else:
                for index, author in enumerate(authors_papers_data['authorlist']):
                    print(f'{index+1}. {author.get("displayName",author["name"])} (name: {author["name"]}, dblp id: {author["dblpid"]})')
        elif command.split()[1] == 'add':
            if len(command.split()) < 3:
                print('Usage: author add <name> <displayName>(optional), use "_" to replace space in name')
            for author in authors_papers_data['authorlist']:
                if author['name'] == command.split()[2]:
                    print(f'Name {command.split()[2]} already existed in authorlist')
                    return True
                if author.get('displayName') == command.split()[2]:
                    print(f'Name "{command.split()[2]}" already existed as displayName in authorlist')
                    return True
                if author['name'] == command.split()[3]:
                    print(f'DisplayName {command.split()[3]} already existed as name in authorlist')
                    return True
                if author.get('displayName') == command.split()[3]:
                    print(f'DisplayName {command.split()[3]} already existed as in authorlist')
                    return True
            new_author = {'name':command.split()[2],'dblpid':'','papers':[]}
            if len(command.split()) >= 4:
                new_author['displayName'] = command.split()[3]
            authors_papers_data['authorlist'].append(new_author)
            print(f'Successfully added author: {new_author.get("displayName",new_author["name"])} (name: {new_author["name"]}) to authorlist')
        elif command.split()[1] == 'info':
            if len(command.split()) < 3:
                print('Usage: author info <name/displayName>')
                return True
            find_flag = False
            for author in authors_papers_data['authorlist']:
                if author['name'] == command.split()[2] or author.get('displayName') == command.split()[2]:
                    find_flag = True
                    print(f'Found author: {author.get("displayName",author["name"])} (name: {author["name"]}, dblp id: {author["dblpid"]})')
                    print(f'{len(author["papers"])} papers found:')
                    for index, paper in enumerate(author['papers']):
                        print(f'{index+1}. {paper["title"]} - ({paper["year"]})\n')
            if find_flag == False:
                print(f'No author found for name/displayName: {command.split()[2]}')
        elif command.split()[1] == 'modify':
            if command.split()[2] == 'displayName':
                if command.split()[3] == 'auto':
                    print('Auto displayName not supported yet')
                elif command.split()[3] == 'set':
                    if command.split()[4] == None:
                        print('Error: no value provided for displayName')
                    else:
                        if author['name'] == command.split()[3]:
                            print(f'DisplayName {command.split()[3]} already existed as name in authorlist')
                        elif author.get('displayName') == command.split()[3]:
                            print(f'DisplayName {command.split()[3]} already existed as in authorlist')
        elif command.split()[1] == 'remove':
            find_flag = False
            for index, author in enumerate(authors_papers_data['authorlist']):
                if author['name'] == command.split()[2] or author.get('displayName') == command.split()[2]:
                    find_flag = True
                    print(
                        f'Found author: {author.get("displayName",author["name"])} (name: {author["name"]})\n'
                        'Are you sure you want to remove this author?\n'
                        f'Please type "remove {author["name"]}" to confirm, or type anything else to cancel.'
                    )
                    surliy=input()
                    if surliy == 'remove ' + author["name"]:
                        print(f'Author {author["name"]} removed from authorlist')
                        authors_papers_data['authorlist'].pop(index)
                    else:
                        print('Operation cancelled')
            if find_flag == False:
                print(f'No author found for name/displayName: {command.split()[2]}')        
        else:
            print('Useage: author <list/add/info/modify/remove> ... Or use "help" command to see available commands')
    elif command.split()[0] == 'exit':
        print('Exiting...')
        return False 
    else:
        print('Unknown command, use "help" command to see available commands')
    return True
                
def main():
    global authors_papers_data
    authors_papers_data, is_jsonfile_load = jsonfile_to_dict('authors_papers_data.json')
    if is_jsonfile_load == False:
        authors_papers_data['authorlist'] = []
    running = True
    print('Welcome to the PaperFinder! Use "help" command to see available commands.')
    while running:
        command = input()
        running = command_processing(command)
        
    dict_to_jsonfile('authors_papers_data.json',authors_papers_data)
    return

if __name__ == '__main__':
    main()
