from typing import Tuple, Optional

class Author:
    def __init__ (self, name:str, display_name:str='', dblpid:str='', papers:Optional['Papers']=None):
        self.name = name
        self.display_name = display_name
        self.dblpid = dblpid
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
        return f'{self.get_shown_name()} (name: {self.name}, dblp id: {self.dblpid})'
    def info(self) -> str:
        info = f'{self.get_shown_name()} (name: {self.name}, dblp id: {self.dblpid})\n'
        info += f'Found {len(self.paper_list)} papers:'
        for index, paper in enumerate(self.paper_list):
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
    def __init__ (self, title:str='', type:str='', year:str='',  author_name_list: Optional[list] = None, 
                ee_list: Optional[list] = None, month:str='', volume:str='', pages:str='', number:str='',
                journal:str='', booktitle:str='', need_manual_check:str=''):
        self.title = title
        self.type = type
        self.year = year
        self.author_name_list = author_name_list or []
        self.ee_list = ee_list or []
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
            booktitle = data.get('booktitle',''),
            need_manual_check = data.get('need_manual_check','')
            )
    
    def to_dict(self, include_empty=False):
        if include_empty:
            return self.__dict__
        else:
            return {k: v for k, v in self.__dict__.items() if v not in (None, '', [], {})}
    def year_month_to_int(self) -> Tuple[int, int]:
        year = int(self.year)

        months_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        if self.month:
            try:
                month = int(self.month)
            except (ValueError, TypeError):
                month = months_map.get(self.month.lower(), 1)  # 默认1月
        else:
            month = 0

        return (year, month)

class Papers:
    def __init__(self, papers_list:list=[]):
        self.papers_list = papers_list

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
        match_status = 'new'
        for paper in self.papers_list:
            if new_paper.title == paper.title and new_paper.type == paper.type :
                match_status = 'same title'
                for ee in new_paper.ee_list:
                   if ee in paper.ee_list:
                        match_status = 'exist'
                        break
                if match_status == 'exist':
                    merged_ee_list = list(set(paper.ee_list + new_paper.ee_list))
                    paper.ee_list = merged_ee_list
                    break

                if (new_paper.journal == paper.journal and paper.journal != ''):
                   match_status = 'same journal'
                if (new_paper.booktitle == paper.booktitle and paper.booktitle != ''):
                    match_status = 'same booktitle'
                if (match_status == 'same journal' or match_status == 'same booktitle'):
                    if((new_paper.volume == paper.volume and paper.volume != '') or
                    (new_paper.pages == paper.pages and paper.pages != '' )or
                    (new_paper.number == paper.number and paper.number != '')):
                       match_status = 'NMC_SDM' # need manual check, suspiciously different metadata
                    else:
                        match_status = 'NMC_UR' # need manual check, unknown relation
                elif new_paper.year == paper.year:
                    match_status = 'NMC_SY_DJ/B' # need manual check, same year, different journal/booktitle
                else:
                    match_status = 'different'
        if match_status == 'exist':
            return False
        else:
            if match_status == 'NMC_SDM':
                new_paper.need_manual_check = 'suspiciously different metadata'
            elif match_status == 'NMC_UR':
                new_paper.need_manual_check = 'unknown relation'
            elif match_status == 'NMC_SY_DJ/B':
                new_paper.need_manual_check = 'same year, different journal/booktitle'
            self.papers_list.append(new_paper) # include 'new' and 'different' match_status
        return True

    def sort(self):
        self.papers_list.sort(key = lambda paper:paper.year_month_to_int(), reverse=True)

    def merge(self,other: 'Papers') -> int:   
        new_papers_count = 0
        for new_paper in other.papers_list:
            new_papers_count += (self.append(new_paper) == True)
        self.sort()
        return new_papers_count
    
    def count(self) -> int:
        return len(self.papers_list)