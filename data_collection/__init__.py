"""Data collection package for Gazzetta scraping and database management."""

from data_collection.scraper_gazzetta import GazzettaBloggerScraper
from data_collection.db.models import Blogger, Article, Category

__all__ = [
    'GazzettaBloggerScraper',
    'Blogger',
    'Article',
    'Category',
]

__version__ = '0.1.0'