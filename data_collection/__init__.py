"""Data collection package for Gazzetta scraping and database management."""

from core.db.models import Article, Blogger, Category
from data_collection.scraper_gazzetta_async import GazzettaBloggerScraper

__all__ = [
    "GazzettaBloggerScraper",
    "Blogger",
    "Article",
    "Category",
]

__version__ = "0.1.0"
