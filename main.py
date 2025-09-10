import requests
import xml.etree.ElementTree as ET
import json
import questionary
import json_file_operations
from ui.cli import run_cli
from models import Author, Paper, Authors
import api.dblp as dblp

                
def main():
    authors = Authors()
    load_success , data_dict = json_file_operations.file_to_dict('authors_papers_data.json')
    if load_success == False or 'authors_list' not in data_dict:
        print('No authors_papers_data.json file found or it\'s format error, creating a new one...')
    else:
        authors = Authors.from_dict(data_dict)
    
    run_cli(authors)

    print('Exiting...')
    data_dict = authors.to_dict()
    json_file_operations.dict_to_file('authors_papers_data.json',data_dict)

if __name__ == '__main__':
    #dblp.test()
    main()
