from typing import Tuple, Optional

class Author:
    def __init__ (self, name:str, display_name:str='', dblpid:str='',oaid:str='', papers:Optional['Papers']=None):
        self.name = name
        self.display_name = display_name
        self.dblpid = dblpid
        self.oaid = oaid
        self.papers = papers or Papers()

    @classmethod
    def from_dict(cls,data:dict):
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'Missing required field {field} in Author data')
        papers = Papers.from_dict(data)
        return cls(
            name = data.get('name',''),
            display_name = data.get('display_name',''),
            dblpid = data.get('dblpid',''),
            oaid = data.get('oaid',''),
            papers = papers
        )
    
    def to_dict(self, include_empty=False):
        result = {}
        for k, v in self.__dict__.items():
            key = 'papers_list' if k == 'papers' else k  # 映射字段名
            if hasattr(v, 'to_list'):
                result[key] = v.to_list(include_empty)
            elif hasattr(v, 'to_dict'):
                result[key] = v.to_dict(include_empty)
            elif include_empty or v not in (None, '', [], {}):
                result[key] = v
        return result
    
    def get_shown_name(self):
        return self.display_name if self.display_name != '' else self.name
    
    def short_info(self) -> str:
        return f'{self.get_shown_name()} (name: {self.name}, dblp id: {self.dblpid}, openAlex id: {self.oaid})'
    def info(self) -> str:
        info = f'{self.get_shown_name()} (name: {self.name}, dblp id: {self.dblpid}, openAlex id: {self.oaid})\n'
        info += f'Found {len(self.papers.papers_list)} papers:'
        for index, paper in enumerate(self.papers.papers_list):
            info += f'\n{index+1}. {paper.title} - ({paper.year})'
        return info
    
    def safe_set_display_name(self, display_name:str) -> Tuple[bool, str]:
        if display_name != '':
            self.display_name = display_name.replace(' ','_')
            return True, f'Scuccessfully set {self.display_name}(name:{self.name}) as display name'

    def safe_set_dblpid(self, dblpid:str) -> Tuple[bool, str]:
        if dblpid.count('/') != 1:
            return False , 'Invalid DBLP ID'
        else:
            self.dblpid = dblpid
            return True, f'Scuccessfully set {dblpid} as {self.get_shown_name()} DBLP ID'        

class Authors:
    def __init__ (self, authors_list:list=[]):
        self.authors_list = authors_list
    
    @classmethod
    def from_dict(cls,data:dict):
        authors_list = [Author.from_dict(author_data) for author_data in data.get('authors_list', [])]
        return cls(authors_list)
    
    @classmethod
    def from_dictlist(cls,data_list:list):
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
            info_list.append(f'{index+1}. {single_author.get_shown_name()} (name: {single_author.name}, dblp id: {single_author.dblpid})')
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
            author_name_list: Optional[list] = None, doi:str='', location:str='', volume:str='',
            number:str='', pages:str='', fwci:str='', need_manual_check:str=''):
        self.title = title
        self.type = type
        self.year = year
        self.month = month
        self.day = day
        self.author_name_list = author_name_list or []
        self.doi = doi
        self.location = location
        self.volume = volume
        self.number = number
        self.pages = pages
        self.fwci = fwci
        self.need_manual_check = need_manual_check

    @classmethod
    def from_dict(cls,data:dict):
        required_fields = ['title','type','year','author_name_list']
        for field in required_fields:
            if field not in data:
                print(f'error date:{data}')
                raise ValueError(f'Missing required field {field} in data')
        allowed_fields = {
        'title', 'type', 'year', 'month', 'day', 'author_name_list',
        'doi', 'location', 'volume', 'number', 'pages', 'fwci', 'need_manual_check'
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
        if self.type == 'preprint':
            return True
        if 'arxiv' in self.doi.lower():
            self.type = 'preprint'
            return True
        if 'corr' in self.location.lower():
            self.type = 'preprint'
            return True
        return False
    
    def cvrp_year_fix(self) -> bool:
        if 'cvpr' in self.location.lower():
            try:
                year = int(self.location[:4])
                if year != self.year:
                    self.location = f'{self.year}{self.location[4:]}'
                    return True
            except ValueError:
                return False
        return False


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
        for new_paper in other.papers_list:
            new_papers_count += (self.append(new_paper) == True)
        self.sort()
        return new_papers_count
    
    def count(self) -> int:
        return len(self.papers_list)