from models import Author, Paper
from api import dblp
from api import openalex as oa
import excel_file_operations as efo

def command_processing(command_list,authors):
    if len(command_list) < 1: return True
    elif command_list[0] == 'help':
        command_help()
    elif command_list[0] == 'author':
        command_author(command_list[1:],authors)
    elif command_list[0] == 'paper':
        command_paper(command_list[1:],authors)
    elif command_list[0] == 'excel':
        command_excel(command_list[1:],authors)
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
            print(target_author.info())
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
            elif command_list[1] == 'dblpid':
                if command_list[2] == 'search':
                    if len(command_list) == 3:
                        print("Searching author...")
                        dblpid_search_loop(target_author.name,target_author)
                    elif len(command_list) == 4:
                        print("Searching author...")
                        dblpid_search_loop(command_list[3],target_author)
                    else:
                        print('Usage: author modify <name/displayName> dblpID search <searchName>(optional) - It will use author\'s name to fetch author\'s dblpID')
                        
                elif command_list[2] == 'set':
                    success , message = target_author.safe_set_dblpid(command_list[3])
                    print(message)
                else:
                    print('Usage: author dblpid [search/set] <dblpid>')
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
                    success , message = target_author.safe_set_dblpid(command_list[3])
                    print(message)
                else:
                    print('Usage: author dblpid [search/set] <searchName/value>')    
            else:
                print('Usage: author modify <name/displayName> [displayName/dblpid/oaid] [search/set] <searchName/value>')
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
def dblpid_search_loop(search_name,target_author):
    result , success , message = dblp.search_author(search_name)
    print(message)
    if not success:
        return
    print(f'prefect hit and full hit:')
    for index , single_author in enumerate(result):
        #single_author['papertitle'] = dblp.find_a_paper_by_dblpid(single_author['dblpid'])
        if(single_author['hit'] == 'partial'):
            break
        print(f'{index+1}. {single_author["name"]} (dblp id: {single_author["dblpid"]}, match type: {single_author["hit"]})')
    
    loop = True
    print('you can use command behind:\n'
            'set <index> - set as the dblpid of the index-th author\n'
            'info <index> - show a paper\'s info of the author with index\n'
            'showall - show all hits\n'
            '<anything else> - cancel modify')
    while loop:
        command = input()
        command_list = command.split()
        if command_list[0] == 'set':
            try: 
                target_author.dblpid = result[int(command_list[1])-1]['dblpid']
                print(f'Successly set the dblpid of {target_author.name} to {target_author.dblpid}') 
                loop = False
            except (ValueError,IndexError,TypeError):
                print('Usage: set <index> - please make sure you input a illegal index')
        elif command_list[0] == 'info':
            print('Getting paper info...')
            title , success = dblp.find_a_paper_by_dblpid(result[int(command_list[1])-1]['dblpid'])
            print(f'One of the papers of {result[int(command_list[1])-1]['name']} is: {title}')
        elif command_list[0] == 'showall':
            for index,single_author in enumerate(result):
                print(f'{index+1}. {single_author['name']} (dblp id: {single_author['dblpid']}, match type: {single_author['hit']})')
        else:
            loop = False
    return
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

def command_paper(command_list,authors):
    if len(command_list) < 1:
        print('Usage: paper <get/update> ... Or use "help" command to see available commands')
    elif command_list[0] == 'get':
        command_paper_get(command_list[1:],authors)
    elif command_list[0] == 'update':
        command_paper_update(command_list[1:],authors)
    else:
        print('Usage: paper <get/update> ... Or use "help" command to see available commands')
def command_paper_get(command_list,authors):
    if len(command_list) > 1 or len(command_list) < 1:
        print('Usage: paper get <name/displayName>(optional) - get papers of author')
    elif len(command_list) == 1:
        target_author , success = authors.find(command_list[0])
        if success:
            print(f'{target_author.get_shown_name()} has {target_author.papers.count()} papers')
        for index , sigle_paper in enumerate(target_author.papers.papers_list):
            print(f'{index+1}. {sigle_paper.title} - ({sigle_paper.year})')
            
def command_paper_update(command_list,authors):
    if len(command_list) > 1:
        print('Usage: paper update <name/displayName>(optional) - update papers of author (or all)')
    elif len(command_list) == 1:
        target_author , success = authors.find(command_list[0])
        if success:
            print(f'Processing...')
            new_papers_count = 0
            if target_author.dblpid == '':
                print(f'{target_author.get_shown_name()} has no dblpID, please use "author modify dblpid [search/set] <value>" to find one')
            else :
                new_papers = dblp.fetch_author_papers(target_author.dblpid)
                new_papers_count += target_author.papers.merge(new_papers)
            if target_author.oaid == '':
                print(f'{target_author.get_shown_name()} has no OpenAlexID, please use "author modify oaid [search/set] <value>" to find one')
            else:
                new_papers = oa.fetch_author_papers(target_author.oaid)
                new_papers_count += target_author.papers.merge(new_papers)
            print(f'Successfully update {new_papers_count} papers of {target_author.get_shown_name()}')
        else:
            print(f'No author found for name/displayName: {command_list[0]}')
    elif len(command_list) == 0:
        print(f'Processing...')
        all_new_papers_count = 0
        for single_author in authors.authors_list:
            if single_author.dblpid == '':
                continue
            else:
                new_papers = dblp.fetch_author_papers(single_author.dblpid)
                new_papers_count = single_author.papers.merge(new_papers)
                all_new_papers_count += new_papers_count
                if new_papers_count != 0:
                    print(f'Successfully update {new_papers_count} papers of {single_author.get_shown_name()}')
        print(f'Successfully update {all_new_papers_count} papers in total')
    
    
def command_excel(command_list,authors):
    if len(command_list) < 1:
        print('Usage: excel output [authors/papers] ... Or use "help" command to see available commands')
    elif command_list[0] == 'output':
        command_excel_output(command_list[1:],authors)
            

def command_excel_output(command_list,authors):
    if len(command_list) < 1 or len(command_list) > 1:
        print('Usage: excel output [authors/papers]')
    elif command_list[0] == 'authors':
        efo.output_authors(authors)
        print('Successfully output all authors')
    elif command_list[0] == 'papers':
        if len(command_list) == 1:
            for single_author in authors.authors_list:
                efo.output_author_papers(single_author)
            print('Successfully output all papers')
        elif len(command_list) == 2:
            target_author , success = authors.find(command_list[1])
            if success:
                efo.output_author_papers(target_author)
                print(f'Successfully output papers of {target_author.get_shown_name()}')
            else:
                print(f'No author found for name/displayName: {command_list[1]}')
        else:
            print('Usage: excel output papers <name/displayName>(optional) - output papers of author (or all)')



def run_cli(authors):
    running=True
    print('Welcome to paperfinder cli, try "help" command to see available commands')
    while running:
        command = input()
        running = command_processing(command.split(),authors)
    return
