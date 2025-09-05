
class Author:
    def __init__ (self, name:str, display_name:str='', dblpid:str='', papers_list:list=[]):
        self.name = name
        self.display_name = display_name
        self.dblpid = dblpid
        self.papers_list = papers_list

    @classmethod
    def from_dict(cls,data:dict):
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'Missing required field {field} in Author data')
        return cls(
            name = data.get('name',''),
            display_name = data.get('display_name',''),
            dblpid = data.get('dblpid',''),
            papers_list = data.get('papers_list',[])
        )
    
    def to_dict(self, include_empty=False):
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                result[k] = [item.to_dict(include_empty) if hasattr(item, 'to_dict') else item for item in v]
            elif hasattr(v, 'to_dict'):
                result[k] = v.to_dict(include_empty)
            elif include_empty or v not in (None, '', [], {}):
                result[k] = v
        return result

class Paper:
    def __init__ (self, title:str='', type:str='', year:str='',  author_name_list:list=[] , ee_list:list=[],
                 month:str='', volume:str='', pages:str='', number:str='', journal:str='', booktitle:str=''):
        self.title = title
        self.type = type
        self.year = year
        self.author_name_list = author_name_list
        self.ee_list = ee_list
        self.month = month
        self.volume = volume
        self.pages = pages
        self.number = number
        self.journal = journal
        self.booktitle = booktitle

    @classmethod
    def from_dict(cls,data:dict):
        required_fields = ['title','type','year','author_name_list','ee_list']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'Missing required field {field} in data')
        return cls(
            title = data.get('title',''),
            type = data.get('type',''),
            year = data.get('year',''),
            author_name_list = data.get('author_name_list',[]),
            ee_list = data.get('ee_list',[]),
            month = data.get('month',''),
            volume = data.get('volume',''),
            pages = data.get('pages',''),
            journal = data.get('journal',''),
            booktitle = data.get('booktitle','')
            )
    
    def to_dict(self, include_empty=False):
        if include_empty:
            return self.__dict__
        else:
            return {k: v for k, v in self.__dict__.items() if v not in (None, '', [], {})}