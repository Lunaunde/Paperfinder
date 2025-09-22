import requests
import xml.etree.ElementTree as ET
import json
import json_file_operations as jfo
import excel_file_operations as efo
from ui.cli import run_cli
from models import Author, Authors, Paper, Papers
import api.dblp as dblp
import api.semantic_scholar as s2
       
def main():
    authors = Authors()
    papers = Papers()
    load_success , data_dict = jfo.file_to_dict('data.json')
    if load_success == True:
        if 'authors_list' in data_dict:
            authors = Authors.from_list(data_dict['authors_list'])
        if 'papers_list' in data_dict:
            papers = Papers.from_list(data_dict['papers_list'])

    run_cli(authors,papers)

    print('Exiting...')
    data_dict = {**authors.to_dict(), **papers.to_dict()}
    jfo.dict_to_file('data.json',data_dict)

if __name__ == '__main__':
    #s2.test()
    main()
