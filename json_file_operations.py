import json
    
def file_to_dict(filename):
    try:
        with open(filename,'r',encoding='utf-8') as file:
            data_dict = json.load(file)
        print(f'Loaded {filename} successfully')
        return True , data_dict
    except FileNotFoundError:
        print(f"Error:file {filename} not found")
    except json.JSONDecodeError as errorinfo:
        print(f'Error:failed to decode JSON from file {filename}, error info:\n{errorinfo}')
    except Exception as errorinfo:
        print(f'Error:an unexpected error occurred while reading file {filename}, error info:\n{errorinfo}')
    return False , {} 

def dict_to_file(filename,data_dict):
    try:
        with open(filename,'w',encoding='utf-8') as file:
            json.dump(data_dict,file,indent=4)
        print(f'Saved {filename} successfully')
        return True
    except Exception as errorinfo:
        print(f'Error:an unexpected error occurred while writing file {filename}, error info:\n{errorinfo}')
        return False