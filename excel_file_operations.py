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
        'dblpid': []
    }
    for author in authors.authors_list:
        data['name'].append(author.name)
        data['display_name'].append(author.display_name)
        data['dblpid'].append(author.dblpid)

    df = pd.DataFrame(data)
    excel_merge('output.xlsx', df, 'authors')

def output_author_papers(author):
    sheet_name = author.name
    data = {
        'title': [],
        'type': [],
        'year': [],
        'authors': [],
        'ee': [],
        'month': [],
        'volume': [],
        'pages': [],
        'number': [],
        'journal': [],
        'booktitle': [],
        'need_manual_check': []
    }
    for paper in author.papers.papers_list:
        data['title'].append(paper.title)
        data['type'].append(paper.type)
        data['year'].append(paper.year)
        author_list_str = ','.join(paper.author_name_list)
        data['authors'].append(author_list_str)
        ee_list_str = ','.join(paper.ee_list)
        data['ee'].append(ee_list_str)

        data['month'].append(paper.month)
        data['volume'].append(paper.volume)
        data['pages'].append(paper.pages)
        data['number'].append(paper.number)
        data['journal'].append(paper.journal)
        data['booktitle'].append(paper.booktitle)
        data['need_manual_check'].append(paper.need_manual_check)

    df = pd.DataFrame(data)
    excel_merge('output.xlsx', df, sheet_name)
    return