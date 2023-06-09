from pydantic import BaseModel
from typing import List
from datetime import datetime, date
from typing import Optional



class NewsBase(BaseModel):
    date: datetime
    link: str
    title: str
    text: str
    preprocessed_text: Optional[str] = ""
    short_text: Optional[str] = ""
    source_id: int


class NewsCreate(NewsBase):
    def __hash__(self):
        return hash((self.date, self.title, self.source_id, self.link))
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.date == other.date
            and self.title == other.title
            and self.source_id == other.source_id
            and self.link == other.link
        )


class NewsCreateList(BaseModel):
    news_list: List[NewsCreate]


class News(NewsBase):
    class Config:
        orm_mode = True



class ClusterCreate(BaseModel):
    date: date
    create_date: Optional[datetime] = datetime.now()
    cluster_num: int
    title: str
    text: str
    keywords: str
    news_ids: List[int]
    sources: List[str]

class ClusterCreateList(BaseModel):
    cluster_list: List[ClusterCreate]

class Cluster(NewsBase):
    class Config:
        orm_mode = True