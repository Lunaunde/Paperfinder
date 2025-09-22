import pandas as pd
import os

def excel_merge(file_name, df, sheet_name):
    if os.path.exists(file_name):
        mode = 'a'
        if_sheet_exists = 'replace'
    else:
        mode = 'w'
        if_sheet_exists = None
    
    with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode, if_sheet_exists=if_sheet_exists) as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

def output_authors(authors):
    data = {
        'name': [],
        'display_name': [],
        'openAlexID': [],
        'coauthor_list': []
    }
    for author in authors.authors_list:
        data['name'].append(author.name)
        data['display_name'].append(author.display_name)
        data['openAlexID'].append(author.oaid)
        data['coauthor_list'].append(author.coauthor_list)

    df = pd.DataFrame(data)
    excel_merge('output.xlsx', df, 'authors')

def output_author_papers(author,author_papers,file_name='output'):
    sheet_name = author
    data = {
        'title': [],
        'type': [],
        'authors': [],
        'year': [],
        'month': [],
        'day': [],
        'doi': [],
        'source': [],
        'volume': [],
        'number': [],
        'pages': [],
        'fwci': [],
        'need_manual_check': []

    }
    for paper in author_papers.papers_list:
        data['title'].append(paper.title)
        data['type'].append(paper.type)
        data['authors'].append(paper.author_name_list)
        data['year'].append(paper.year)
        data['month'].append(paper.month)
        data['day'].append(paper.day)
        data['doi'].append(paper.doi)
        data['source'].append(paper.source)
        data['volume'].append(paper.volume)
        data['number'].append(paper.number)
        data['pages'].append(paper.pages)
        data['fwci'].append(paper.fwci)
        data['need_manual_check'].append(paper.need_manual_check)

    df = pd.DataFrame(data)
    excel_merge(f'{file_name}.xlsx', df, sheet_name)
    return