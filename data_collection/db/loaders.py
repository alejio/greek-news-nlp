from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from rich import print as rprint
from sqlalchemy.exc import IntegrityError

from data_collection.db.models import Blogger, Article, Category

class BaseLoader:
    def __init__(self, db: Session):
        self.db = db
        self.category_map = {}

    def get_or_create_category(self, cat_name: str) -> Category:
        """Get an existing category or create a new one.
        
        Args:
            cat_name: The name of the category
            
        Returns:
            Category: The existing or newly created category
        """
        # First check our local cache
        if cat_name in self.category_map:
            return self.category_map[cat_name]
        
        # Then check the database
        category = self.db.query(Category).filter_by(name=cat_name).first()
        if not category:
            # Only create if it doesn't exist
            category = Category(name=cat_name)
            self.db.add(category)
            self.db.flush()
        
        # Cache the result
        self.category_map[cat_name] = category
        return category

    def get_or_create_blogger(self, name: str, profile_url: str = '') -> Blogger:
        """Get an existing blogger or create a new one.
        
        Args:
            name: The name of the blogger
            profile_url: The profile URL of the blogger (optional)
            
        Returns:
            Blogger: The existing or newly created blogger
        """
        blogger = self.db.query(Blogger).filter_by(name=name).first()
        if not blogger:
            blogger = Blogger(
                name=name,
                profile_url=profile_url
            )
            self.db.add(blogger)
            self.db.flush()
        return blogger

class ScrapedArticlesLoader(BaseLoader):
    def parse_date(self, date_str: str) -> datetime:
        """Parse date formats:
        - DD/MM/YYYY
        - DD/MM/YYYY - HH:MM
        """
        try:
            # First try with time
            return datetime.strptime(date_str, "%d/%m/%Y - %H:%M")
        except ValueError:
            try:
                # Then try just date
                return datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                rprint(f"[yellow]Warning: Could not parse date {date_str}, using current time[/yellow]")
                return datetime.utcnow()

    def process_article(self, article_data: Dict[str, Any]):
        """Process a single article from scraped data.
        
        Args:
            article_data: Dictionary containing article information
        """
        try:
            # Check if article already exists
            existing_article = self.db.query(Article).filter_by(
                article_url=article_data.get('article_url', '')
            ).first()
            
            if existing_article:
                rprint(f"[yellow]Article already exists: {article_data.get('title', 'Unknown')}[/yellow]")
                return

            # Get or create blogger
            blogger = self.get_or_create_blogger(article_data['blogger_name'])

            # Process categories
            article_categories = [
                self.get_or_create_category(cat_name)
                for cat_name in article_data.get('categories', [])
            ]

            # Create article
            article = Article(
                blogger=blogger,
                title=article_data['title'],
                content=article_data['content'],
                article_url=article_data.get('article_url', ''),
                published_date=self.parse_date(article_data['date']),
                categories=article_categories
            )
            self.db.add(article)
            self.db.flush()

        except IntegrityError:
            self.db.rollback()
            rprint(f"[yellow]Skipping duplicate article: {article_data.get('title', 'Unknown')}[/yellow]")
        except Exception as e:
            rprint(f"[red]Error processing article: {e}[/red]")
            raise

class GazzettaBloggersLoader(BaseLoader):
    def parse_date(self, date_str: str) -> datetime:
        """Parse date formats:
        - YYYY-MM-DD HH:MM:SS
        - DD/MM/YYYY - HH:MM
        """
        try:
            # First try the original format
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Then try the new format
                return datetime.strptime(date_str, "%d/%m/%Y - %H:%M")
            except ValueError:
                rprint(f"[yellow]Warning: Could not parse date {date_str}, using current time[/yellow]")
                return datetime.utcnow()

    def process_article(self, article_data: Dict[str, Any]):
        """Process a single article from Gazzetta data.
        
        Args:
            article_data: Dictionary containing article information
        """
        try:
            # Check if article already exists
            existing_article = self.db.query(Article).filter_by(
                article_url=article_data.get('article_url', '')
            ).first()
            
            if existing_article:
                rprint(f"[yellow]Article already exists: {article_data.get('title', 'Unknown')}[/yellow]")
                return

            # Get or create blogger
            blogger = self.get_or_create_blogger(
                name=article_data.get('blogger_name', ''),
                profile_url=article_data.get('profile_url', '')
            )

            # Process categories
            article_categories = [
                self.get_or_create_category(cat_name)
                for cat_name in article_data.get('categories', [])
            ]

            # Create article
            article = Article(
                blogger=blogger,
                title=article_data['title'],
                content=article_data['content'],
                article_url=article_data.get('article_url', ''),
                published_date=self.parse_date(article_data['date']),
                categories=article_categories
            )
            self.db.add(article)
            self.db.flush()

        except IntegrityError:
            self.db.rollback()
            rprint(f"[yellow]Skipping duplicate article: {article_data.get('title', 'Unknown')}[/yellow]")
        except Exception as e:
            rprint(f"[red]Error processing article: {e}[/red]")
            raise

def load_data(db: Session, file_path: Path, loader_class):
    """Generic function to load data using the specified loader.
    
    Args:
        db: SQLAlchemy database session
        file_path: Path to the JSON data file
        loader_class: Class to use for loading the data (ScrapedArticlesLoader or GazzettaBloggersLoader)
    """
    loader = loader_class(db)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if loader_class == GazzettaBloggersLoader:
        # Handle nested structure for GazzettaBloggersLoader
        total_articles = sum(len(blogger['articles']) for blogger in data)
        processed = 0
        
        for blogger_data in data:
            try:
                for article in blogger_data['articles']:
                    # Add blogger info to each article
                    article['blogger_name'] = blogger_data['name']
                    article['profile_url'] = blogger_data['profile_url']
                    
                    loader.process_article(article)
                    processed += 1
                    
                    if processed % 100 == 0:  # Progress update every 100 articles
                        rprint(f"[green]Processed {processed}/{total_articles} articles[/green]")
                        db.commit()  # Intermediate commit
            except Exception as e:
                rprint(f"[red]Error processing article {processed}/{total_articles}: {e}[/red]")
                db.rollback()
                continue
    else:
        # Original handling for other loaders
        total = len(data)
        for i, article_data in enumerate(data, 1):
            try:
                loader.process_article(article_data)
                if i % 100 == 0:  # Progress update every 100 articles
                    rprint(f"[green]Processed {i}/{total} articles[/green]")
                    db.commit()  # Intermediate commit
            except Exception as e:
                rprint(f"[red]Error processing article {i}/{total}: {e}[/red]")
                db.rollback()
                continue

    db.commit()
    rprint(f"[green]Successfully processed all articles![/green]")