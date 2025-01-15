"""Script to predict stance of articles and save to database."""
import typer
import os
from openai import OpenAI
from rich import print as rprint
from rich.progress import track
from sqlalchemy import select, func
from typing import Optional, Tuple
from datetime import datetime
from rich.table import Table

from data_collection.db.db_config import get_db
from data_collection.db.models import Article, StancePrediction

app = typer.Typer()

def classify_article_with_explanation(client: OpenAI, article_text: str, target_club: str) -> Tuple[str, str]:
    """Classifies the stance of an article towards a target club."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "developer",
                "content": (
                    "Είσαι ένας βοηθός ανάλυσης κειμένου για ελληνικά κείμενα. "
                    "Θέλω να αναλύσεις το παρακάτω απόσπασμα και να προσδιορίσεις "
                    f"αν η στάση του κειμένου απέναντι στην ομάδα {target_club} "
                    "είναι θετική, αρνητική, ή ουδέτερη. "
                    "Στη συνέχεια, εξήγησε σε μία σύντομη παράγραφο γιατί κατέληξες σε αυτό το συμπέρασμα."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Απόσπασμα:\n{article_text}\n\n"
                    "Πρώτα γράψε μόνο μία λέξη (θετική, αρνητική ή ουδέτερη), "
                    "και μετά δώσε μια σύντομη εξήγηση (μία πρόταση) για τη συλλογιστική σου."
                ),
            },
        ],
        temperature=0.0,
        max_tokens=200
    )

    full_reply = response.choices[0].message.content.strip()
    lines = full_reply.split('\n', 1)
    
    if len(lines) == 1:
        stance = lines[0].strip()
        justification = ""
    else:
        stance = lines[0].strip()
        justification = lines[1].strip()

    return stance, justification

@app.command()
def predict(
    target_club: str = typer.Option(..., "--club", "-c", help="Target club for stance analysis"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Number of articles to process in each batch"),
    limit: int = typer.Option(None, "--limit", "-l", help="Limit the number of articles to process"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-prediction of articles that already have predictions"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="OpenAI API key")
):
    """Predict stance for articles in the database."""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    elif not os.getenv("OPENAI_API_KEY"):
        api_key = typer.prompt("OpenAI API key", hide_input=True)
        os.environ["OPENAI_API_KEY"] = api_key

    client = OpenAI()
    db = next(get_db())

    try:
        # Query to get articles that don't have predictions for this target_club
        query = select(Article)
        if not force:
            query = query.outerjoin(
                StancePrediction,
                (Article.id == StancePrediction.article_id) & 
                (StancePrediction.target_club == target_club)
            ).where(StancePrediction.id.is_(None))
        
        # Add random ordering and limit
        query = query.order_by(func.random())
        if limit:
            query = query.limit(limit)
        
        articles = db.execute(query).scalars().all()
        
        if not articles:
            rprint("[yellow]No articles found to process[/yellow]")
            return

        rprint(f"[green]Found {len(articles)} articles to process[/green]")

        # Process articles in batches
        for article in track(articles, description="Processing articles..."):
            try:
                stance, justification = classify_article_with_explanation(
                    client, 
                    article.content, 
                    target_club
                )
                
                # Check if prediction exists and update it, or create new one
                prediction = db.query(StancePrediction).filter_by(
                    article_id=article.id,
                    target_club=target_club
                ).first()
                
                if prediction and force:
                    prediction.stance = stance
                    prediction.justification = justification
                    prediction.created_at = datetime.utcnow()
                else:
                    prediction = StancePrediction(
                        article_id=article.id,
                        target_club=target_club,
                        stance=stance,
                        justification=justification
                    )
                    db.add(prediction)
                
                # Commit every batch_size articles
                if articles.index(article) % batch_size == 0:
                    db.commit()
                    rprint(f"[green]Processed {articles.index(article)} articles[/green]")
                
            except Exception as e:
                rprint(f"[red]Error processing article {article.id}: {e}[/red]")
                db.rollback()
                continue

        # Final commit
        db.commit()
        rprint("[bold green]Successfully processed all articles![/bold green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        db.close()

@app.command()
def list_predictions(
    target_club: Optional[str] = typer.Option(None, "--club", "-c", help="Filter by target club")
):
    """List existing predictions in the database."""
    db = next(get_db())
    
    try:
        query = select(StancePrediction.target_club, 
                      func.count(StancePrediction.id).label('count'))
        
        if target_club:
            query = query.where(StancePrediction.target_club == target_club)
            
        query = query.group_by(StancePrediction.target_club)
        
        results = db.execute(query).all()
        
        if not results:
            rprint("[yellow]No predictions found[/yellow]")
            return
            
        table = Table(title="Stance Predictions")
        table.add_column("Target Club")
        table.add_column("Count")
        
        for club, count in results:
            table.add_row(club, str(count))
            
        rprint(table)
        
    finally:
        db.close()

if __name__ == "__main__":
    app() 