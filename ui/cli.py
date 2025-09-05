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
def run_cli():
    running=True
    while running:
        command = input()
        running = command_processing(command)
