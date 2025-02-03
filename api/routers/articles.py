"""Article-related routes."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db.config import get_db
from core.db.models import Article, Blogger, Category, StancePrediction

router = APIRouter()

# Pydantic models for response
class StancePredictionResponse(BaseModel):
    target: str
    target_type: str
    stance: str
    justification: Optional[str]

    class Config:
        from_attributes = True

class BloggerResponse(BaseModel):
    name: str
    profile_url: str

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    article_url: str
    published_date: Optional[datetime]
    blogger: BloggerResponse
    categories: List[CategoryResponse]
    stance_predictions: List[StancePredictionResponse]

    class Config:
        from_attributes = True

@router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = Query(0, description="Number of articles to skip"),
    limit: int = Query(10, description="Number of articles to return"),
    target: Optional[str] = Query(None, description="Filter by target (e.g. team name or referee)"),
    target_type: Optional[str] = Query(None, description="Filter by target type (club or referee)"),
    stance: Optional[str] = Query(None, description="Filter by stance"),
    db: Session = Depends(get_db)
):
    """Get articles with their stance predictions.
    
    Args:
        skip: Number of articles to skip (pagination)
        limit: Number of articles to return (pagination)
        target: Optional filter by target (e.g. team name or referee)
        target_type: Optional filter by target type (club or referee)
        stance: Optional filter by stance
        db: Database session
    
    Returns:
        List of articles with their stance predictions
    """
    query = db.query(Article)

    # Apply filters if provided
    if any([target, target_type, stance]):
        query = query.join(StancePrediction)
        
        if target:
            query = query.filter(StancePrediction.target == target)
        if target_type:
            query = query.filter(StancePrediction.target_type == target_type)
        if stance:
            query = query.filter(StancePrediction.stance == stance)

    # Add joins for eager loading
    query = (
        query
        .join(Blogger)
        .join(Article.categories)
        .join(Article.stance_predictions)
        .distinct()
        .order_by(Article.published_date.desc())
        .offset(skip)
        .limit(limit)
    )

    return query.all() 