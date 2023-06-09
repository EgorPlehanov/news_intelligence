from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Table
from sqlalchemy.orm import relationship



# Таблица "Cluster" (Кластеры новостей)
class Cluster(Base):
    __tablename__ = 'clusters'

    cluster_id = Column(Integer, primary_key=True)
    date = Column(Date)
    create_date = Column(DateTime)
    cluster_num = Column(Integer)
    title = Column(String)
    summary = Column(String)
    keywords = Column(String)

    sources = relationship('Source', secondary='cluster_sources', overlaps='clusters')
    news = relationship('News', secondary='news_clusters', overlaps='clusters')


# Таблица "Source" (Новостные источники)
class Source(Base):
    __tablename__ = 'sources'

    source_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    link = Column(String)

    clusters = relationship('Cluster', secondary='cluster_sources', overlaps='sources')
    news = relationship('News', back_populates='source')


# Таблица "News" (Новости)
class News(Base):
    __tablename__ = 'news'

    news_id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    link = Column(String)
    title = Column(String)
    text = Column(String)
    preprocessed_text = Column(String)
    short_text = Column(String)

    source_id = Column(Integer, ForeignKey('sources.source_id'))

    source = relationship('Source', back_populates='news')
    clusters = relationship('Cluster', secondary='news_clusters')


# Таблица "NewsCluster" (Связка кластеров новостей и новостей)
news_clusters = Table('news_clusters', Base.metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.cluster_id')),
    Column('news_id', Integer, ForeignKey('news.news_id'))
)


# Таблица "ClusterSource" (Связка кластеров и источников)
cluster_sources = Table('cluster_sources', Base.metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.cluster_id')),
    Column('source_id', Integer, ForeignKey('sources.source_id'))
)
