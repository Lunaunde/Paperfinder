from models import Author, Paper, Papers
from api import dblp
from api import openalex as oa
import excel_file_operations as efo
import time

def command_processing(command_list,authors,papers):
    if len(command_list) < 1: return True
    elif command_list[0] == 'help':
        command_help()
    elif command_list[0] == 'author':
        command_author(command_list[1:],authors)
    elif command_list[0] == 'paper':
        command_paper(command_list[1:],authors,papers)
    elif command_list[0] == 'excel':
        command_excel(command_list[1:],authors,papers)
    elif command_list[0] == 'exit':
        return False
    else:
        print('Unknown command, use "help" command to see available commands')
    return True

def command_help():
    print(
    'Commands:\n'
    '0. exit - exit program\n'
    '1. author\n'
    'author list - show mainly info of all authors in list\n'
    'author add <name> <displayName>(optional) - add a new author to authorlist, use "_" to replace space in name\n'
    'author info <name/displayName> - get author info by name\n'
    'author modify <name/displayName> [displayName/dblpid/oaid] [search/set] <searchName/value> - modify author info by name.\n'
    'author remove <name> - remove an author from authorlist by name\n'
    '2. paper\n'
    'paper list - list all papers in paperlist\n'
    'paper get <name/displayName> - get papers of author by name\n'
    'paper update <name/displayName>(optional) - update papers of author (or all)\n'
    '3. excel\n'
    'excel output [authors/papers] <name/displayName>(optional) - output authors list or papers list to excel\n'
)

def command_author(command_list,authors):
    if len(command_list)<1:
        print('Useage: author <list/add/info/modify/remove> ... Or use "help" command to see available commands')
    elif command_list[0] == 'list':
        command_author_list(authors)
    elif command_list[0] == 'add':
        command_author_add(command_list[1:],authors)
    elif command_list[0] == 'info':
        command_author_info(command_list[1:],authors)
    elif command_list[0] == 'modify':
        command_author_modify(command_list[1:],authors)
    elif command_list[0] == 'remove':
        command_author_remove(command_list[1:],authors)
    else:
        print('Usage: author <list|add|info|modify|remove> ... Or use "help" command to see available commands')
    return  
def command_author_list(authors):
    if authors.count() == 0:
        print('No author in authorlist, use "author add ..." to add a new author')
    else:
        for info in authors.info_list():
            print(info)
    return
def command_author_add(command_list,authors):
    if len(command_list) < 1 or len(command_list) > 2:
        print('Usage: author add <name> <displayName>(optional), use "_" to replace space in name')
    elif len(command_list) == 1:
        success , message = authors.append(Author(command_list[0]))
    elif len(command_list) == 2:
        success , message = authors.append(Author(command_list[0],command_list[1]))
    print(message)
    return
def command_author_info(command_list,authors):
    if len(command_list) < 1 or len(command_list) > 1:
        print('Usage: author info <name/displayName>')
    else:
        target_author , success = authors.find(command_list[0])
        if success:
            print(target_author.short_info())
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
def command_author_modify(command_list,authors):
    if len(command_list) < 3 or len(command_list) > 4:
        print('Usage: author modify <name/displayName> [displayName/dblpid/oaid] [search/set] <searchName/value>')
    else:
        target_author , success = authors.find(command_list[0])
        if success: 
            if command_list[1] == 'displayName':
                if command_list[2] == 'search':
                    print('Search displayName not supported yet')
                elif command_list[2] == 'set':
                    success , message = target_author.safe_set_display_name(command_list[3])
                    if success:
                        print(message)
                else:
                    print('Usage: author displayName [set] <displayName>]')
            elif command_list[1] == 'oaid':
                if command_list[2] == 'search':
                    if len(command_list) == 3:
                        print("Searching author...")
                        oaid_search(target_author.name,target_author)
                    elif len(command_list) == 4:
                        print("Searching author...")
                        oaid_search(command_list[3],target_author)
                    else:
                        print('Usage: author modify <name/displayName> oaid search <searchName>(optional) - It will use author\'s name to fetch author\'s dblpID')        
                elif command_list[2] == 'set':
                    success , message = target_author.set_oaid(command_list[3])
                    print(message)
                else:
                    print('Usage: author dblpid [search/set] <searchName/value>')    
            else:
                print('Usage: author modify <name/displayName> [displayName/dblpid/oaid] [search/set] <searchName/value>')
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
def oaid_search(search_name,target_author):
    result , success , message = oa.search_author_id(search_name)
    print(message)
    if not success:
        return
    else:
        target_author.oaid = result
    return
def command_author_remove(command_list,authors):
    if len(command_list) < 1 or len(command_list) > 1:
        print('Usage: author remove <name/displayName>')
    else:
        target_author , success = authors.find(command_list[0])
        if success:
            print(f'Find author: {target_author.short_info()}. Are you sure to remove him/her/it?')
            surely = input(f'type: "remove {target_author.name}" to remove it or type anything else to cancel.\n')
            if surely == 'remove ' + target_author.name:
                authors.remove(target_author)
                print(f'Successful remove {command_list[0]}')
            else:
                print('Canceled')
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
def command_paper(command_list,authors,papers):
    if len(command_list) < 1:
        print('Usage: paper <get/update> ... Or use "help" command to see available commands')
    elif command_list[0] == 'list':
        command_paper_list(command_list[1:],papers)
    elif command_list[0] == 'get':
        command_paper_get(command_list[1:],authors,papers)
    elif command_list[0] == 'update':
        command_paper_update(command_list[1:],authors,papers)
    else:
        print('Usage: paper <get/update> ... Or use "help" command to see available commands')
def command_paper_list(command_list,papers):
    if len(command_list) > 0:
        print('Usage: paper list - list all papers')
        return
    for index,paper in enumerate(papers.papers_list):
        print(f'{index+1}. {paper.short_info()}')
    return
def command_paper_get(command_list,authors,papers):
    if len(command_list) > 1 or len(command_list) < 1:
        print('Usage: paper get <name/displayName> - get papers of author')
    elif len(command_list) == 1:
        target_author , success = authors.find(command_list[0])
        if success:
            author_papers = Papers()
            author_papers = papers.get_auther_paper(target_author.name)
        
            print(f'{target_author.get_shown_name()} has {author_papers.count()} papers')
            for index,single_paper in enumerate(author_papers.papers_list):
                    print(f'{index+1}. {single_paper.short_info()}')
            
def command_paper_update(command_list,authors,papers):
    if len(command_list) > 1:
        print('Usage: paper update <name/displayName>(optional) - update papers of author (or all)')
    elif len(command_list) == 1:
        target_author , success = authors.find(command_list[0])
        if success:
            print(f'Processing...')
            new_papers_count = paper_update(target_author,papers)
            print(f'Successfully update {new_papers_count} papers of {target_author.get_shown_name()}')
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
    elif len(command_list) == 0:
        print(f'Processing...')
        all_new_papers_count = 0
        for single_author in authors.authors_list:
            new_papers_count = paper_update(single_author,papers)
            all_new_papers_count += new_papers_count
            print(f'Successfully update {new_papers_count} papers of {single_author.get_shown_name()}')
        print(f'Successfully update {all_new_papers_count} papers in total')

def paper_update(author,papers):
    new_papers_count = 0
    raw_papers = Papers()
    if len(author.coauthor_list) == 0:
        success , message = oa.build_initial_coauthor_list(author)
        if success == False:
            print(message)
    new_papers = Papers()
    new_papers,message = dblp.fetch_author_papers_by_name(author.name)
    raw_papers.merge(new_papers)
    new_papers,message = oa.fetch_author_papers(author.oaid)
    raw_papers.merge(new_papers)
    if raw_papers != None:
        raw_papers.paper_screening(author)
        new_papers_count += papers.merge(raw_papers)
    else:
        print(message)
    return new_papers_count
    
    
def command_excel(command_list,authors,papers):
    if len(command_list) < 1:
        print('Usage: excel output [authors/papers] ... Or use "help" command to see available commands')
    elif command_list[0] == 'output':
        command_excel_output(command_list[1:],authors,papers)
    else:
        print('Usage: excel output [authors/papers] ... Or use "help" command to see available commands')
            

def command_excel_output(command_list,authors,papers):
    if len(command_list) < 1 or len(command_list) > 2:
        print('Usage: excel output [authors/papers]')
    elif command_list[0] == 'authors':
        efo.output_authors(authors)
        print('Successfully output all authors')
    elif command_list[0] == 'papers':
        if len(command_list) == 1:
            for single_author in authors.authors_list:
                efo.output_author_papers(single_author.name,papers)
            print('Successfully output all papers')
        elif len(command_list) == 2:
            efo.output_author_papers(command_list[1],papers)
            print(f'Successfully output papers of {command_list[1]}')
        else:
            print('Usage: excel output papers <name/displayName>(optional) - output papers of author (or all)')
    else:
        print('Usage: excel output [authors/papers]')



def run_cli(authors,papers):
    running=True
    print('Welcome to paperfinder cli, try "help" command to see available commands')
    while running:
        command = input()
        running = command_processing(command.split(),authors,papers)
    return
