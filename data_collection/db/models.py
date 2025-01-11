# db/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, MetaData
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Association table for article categories
article_categories = Table(
    'article_categories',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Blogger(Base):
    __tablename__ = 'bloggers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    profile_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship("Article", back_populates="blogger")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship("Article", secondary=article_categories, back_populates="categories")

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    blogger_id = Column(Integer, ForeignKey('bloggers.id'))
    title = Column(Text, nullable=False)
    content = Column(Text)
    article_url = Column(Text, nullable=False, unique=True)
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    blogger = relationship("Blogger", back_populates="articles")
    categories = relationship("Category", secondary=article_categories, back_populates="articles")