import requests
import xml.etree.ElementTree as ET
import json
import questionary
import json_file_operations
from ui.cli import run_cli

def load_xml_optional_subele(target_dict,element,subele_name):
    if element.find(subele_name) != None:
        target_dict[subele_name] = element.find(subele_name).text
    return

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
    load_success,data_dict=json_file_operations.file_to_dict('authors_papers_data.json')
    author_list = data_dict['author_list']
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
    data_dict['author_list'] = author_list.to_dict()
    json_file_operations.dict_to_file('authors_papers_data.json',data_dict)

if __name__ == '__main__':
    main()
