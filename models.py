import copy
from typing import Tuple, Optional

class Author:
    def __init__ (self, name:str, display_name:str='', dblpid:str='',oaid:str='',coauthor_list:Optional[list]=None):
        self.name = name
        self.display_name = display_name
        self.dblpid = dblpid
        self.oaid = oaid
        self.coauthor_list = coauthor_list or []

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
            oaid = data.get('oaid',''),
            coauthor_list = data.get('coauthor_list',[])
        )
    
    def to_dict(self, include_empty=False):
        result = {}
        for k, v in self.__dict__.items():
            if hasattr(v, 'to_list'):
                result[k] = v.to_list(include_empty)
            elif hasattr(v, 'to_dict'):
                result[k] = v.to_dict(include_empty)
            elif include_empty or v not in (None, '', [], {}):
                result[k] = v
        return result
    
    def get_shown_name(self):
        return self.display_name if self.display_name != '' else self.name
    
    def short_info(self) -> str:
        return f'{self.get_shown_name()} (name: {self.name}, dblp id: {self.dblpid}, openAlex id: {self.oaid})'
    
    def safe_set_display_name(self, display_name:str) -> Tuple[bool, str]:
        if display_name != '':
            self.display_name = display_name.replace(' ','_')
            return True, f'Successfully set {self.display_name}(name:{self.name}) as display name'     
    def set_oaid(self, oaid:str):
        self.oaid = oaid
        return True, f'Successfully set {self.name} as oaid'
    def add_name_to_coauthor_list(self,author_name:str):
        if author_name != self.name:
            if author_name not in self.coauthor_list:
                self.coauthor_list.append(author_name)
                return True
        return False
    
class Authors:
    def __init__ (self, authors_list:list=[]):
        self.authors_list = authors_list
    
    @classmethod
    def from_dict(cls,data:dict):
        authors_list = [Author.from_dict(author_data) for author_data in data.get('authors_list', [])]
        return cls(authors_list)
    
    @classmethod
    def from_list(cls,data_list:list):
        authors_list = [Author.from_dict(author_data) for author_data in data_list]
        return cls(authors_list)

    def to_dict(self, include_empty=False):
        dict={'authors_list':[]}
        for single_author in self.authors_list:
            dict['authors_list'].append(single_author.to_dict(include_empty))
        return dict
    
    def count(self) -> int:
        return len(self.authors_list)
    
    def info_list(self) -> list:
        info_list = []
        for index , single_author in enumerate(self.authors_list):
            info_list.append(f'{index+1}. {single_author.short_info()}')
        return info_list
    def append(self, new_author:Author) -> Tuple[bool,str]:
        for single_author in self.authors_list:
            if single_author.name == new_author.name:
                return False , f'The name of {new_author.name} already exists'
            if single_author.display_name == new_author.display_name and new_author.display_name != '':
                return False , f'The display name of {new_author.display_name} already exists'
            if single_author.name == new_author.display_name :
                return False , f'The display name of {new_author.display_name} already exists as name'
            if single_author.display_name == new_author.name and new_author.display_name != '':
                return False , f'The name of {new_author.name} already exists as display name'
        self.authors_list.append(new_author)
        return True , f'{new_author.get_shown_name()} added successfully'
    def find(self, author_name:str) -> Tuple[Optional[Author],bool]:
        search_name = author_name.lower()
        for single_author in self.authors_list:
            if single_author.name.lower() == search_name or single_author.get_shown_name().lower() == search_name:
                return single_author , True
        return None , False
    
    def remove(self, author: Author) -> bool:
        try:
            self.authors_list.remove(author)
            return True
        except ValueError:
            return False
    
    def remove_by_name(self, author_name: str) -> bool:
        author, success = self.find(author_name)
        if success:
            return self.remove(author)
        return False


class Paper:
    def __init__ (self, title:str='', type:str='', year:str='', month:str='', day:str='' , 
            author_name_list: Optional[list] = None, doi:str='', source:str='', volume:str='',
            number:str='', pages:str='', fwci:str='', need_manual_check:str=''):
        self.title = title
        self.type = type
        self.year = year
        self.month = month
        self.day = day
        self.author_name_list = author_name_list or []
        self.doi = doi
        self.source = source
        self.volume = volume
        self.number = number
        self.pages = pages
        self.fwci = fwci
        self.need_manual_check = need_manual_check

    @classmethod
    def from_dict(cls,data:dict):
        required_fields = ['title','year','author_name_list']
        for field in required_fields:
            if field not in data:
                print(f'error date:{data}')
                raise ValueError(f'Missing required field {field} in data')
        allowed_fields = {
        'title', 'type', 'year', 'month', 'day', 'author_name_list',
        'doi', 'source', 'volume', 'number', 'pages', 'fwci', 'need_manual_check'
        }
    
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
    
        return cls(**filtered_data)
    
    def to_dict(self, include_empty=False):
        if include_empty:
            return self.__dict__
        else:
            return {k: v for k, v in self.__dict__.items() if v not in (None, '', [], {})}
    def year_month_day_to_int(self) -> Tuple[int, int, int]:

        if self.year:
            year = int(self.year)
        else:
            year = 0

        if self.month:
            month = int(self.month)
        else:
            month = 0

        if self.day:
            day = int(self.day)
        else:
            day = 0

        return (year, month , day)
    
    def update(self, new_paper:'Paper'):
        for key, value in new_paper.__dict__.items():
            if value:
                setattr(self, key, value)

    def tag_preprint(self):
        try:
            if self.type == 'preprint':
                return True
            if 'arxiv' in self.doi.lower():
                self.type = 'preprint'
                return True
            if isinstance(self.source, list):
                for single_source in self.source:
                    if 'corr' in single_source.lower():
                        self.type = 'preprint'
                        return True
            else:
                if 'corr' in self.source.lower():
                    self.type = 'preprint'
                    return True
            return False
        except Exception as e:
            print(self.source)
    
    def cvpr_year_fix(self) -> bool:
        if 'cvpr' in self.source.lower():
            try:
                year = int(self.source[:4])
                if year != self.year:
                    self.source = f'{self.year}{self.source[4:]}'
                    return True
            except ValueError:
                return False
        return False
    
    def short_info(self) -> str:
        return f'{self.title}({self.type}) - ({self.year})'


class Papers:
    def __init__(self, papers_list: Optional[list] = None):
        self.papers_list = papers_list or []

    @classmethod
    def from_dict(cls,data:dict):
        papers_list = []
        for paper_data in data.get('papers_list' , []):
            papers_list.append(Paper.from_dict(paper_data))
        return cls(papers_list)
    
    @classmethod
    def from_list(cls,data_list:list):
        papers_list = []
        for paper_data in data_list:
            papers_list.append(Paper.from_dict(paper_data))
        return cls(papers_list)
    
    def to_list(self,include_empty=False) -> list:
        list = []
        for single_paper in self.papers_list:
            list.append(single_paper.to_dict(include_empty))
        return list
    
    def to_dict(self, include_empty=False):
        dict={'papers_list':[]}
        for single_paper in self.papers_list:
            dict['papers_list'].append(single_paper.to_dict(include_empty))
        return dict
    
    def append(self,new_paper:Paper) -> bool:
        for paper in self.papers_list:
            if new_paper.title == paper.title :
                if new_paper.type == paper.type and new_paper.type == 'preprint':
                    if new_paper.doi == paper.doi:
                        return False
                    if new_paper.year_month_day_to_int() > paper.year_month_day_to_int():
                        paper.update(new_paper)
                        return False
                    else:
                        return False
                elif new_paper.type == 'preprint' and paper.type != 'preprint':
                    return False
                elif new_paper.type != 'preprint' and paper.type == 'preprint':
                    paper.update(new_paper)
                    return False
                elif new_paper.type != paper.type:
                    continue
                else:
                    if new_paper.doi == paper.doi:
                        return False
                    else:
                        new_paper.need_manual_check = 'True'
                        
        self.papers_list.append(new_paper) 
        return True

    def sort(self):
        self.papers_list.sort(key = lambda paper:paper.year_month_day_to_int(), reverse=True)

    def merge(self,other: 'Papers') -> int:   
        new_papers_count = 0
        if other == None:
            return 0
        for new_paper in other.papers_list:
            new_papers_count += (self.append(new_paper) == True)
        self.sort()
        return new_papers_count
    
    def count(self) -> int:
        return len(self.papers_list)
    
    def paper_screening(self,author:Author):
        raw_papers_list = copy.deepcopy(self.papers_list)
        self.papers_list.clear()
        while True:
            count = 0
            for i in range(len(raw_papers_list) - 1, -1, -1):
                if author.name.replace('_',' ') in raw_papers_list[i].author_name_list:
                    for author_name in raw_papers_list[i].author_name_list:
                        if author_name in author.coauthor_list:
                            self.append(raw_papers_list[i])
                            for new_coauthor in raw_papers_list[i].author_name_list:
                                author.add_name_to_coauthor_list(new_coauthor)
                            raw_papers_list.pop(i)
                            count += 1
                            break
            if count == 0: 
                break
        return len(self.papers_list)
    
    def get_auther_paper(self,name:str)->'Papers':
        name = name.replace('_',' ')
        result = Papers()
        
        for single_paper in self.papers_list:
            if name in single_paper.author_name_list:
                result.append(single_paper)

        return result