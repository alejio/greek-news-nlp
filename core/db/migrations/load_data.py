from pathlib import Path

import typer
from rich import print as rprint

from core.db.config import get_db
from core.db.loaders import (
    GazzettaBloggersLoader,
    ScrapedArticlesLoader,
    load_data,
)

app = typer.Typer()


@app.command()
def load_scraped_articles(
    data_dir: str = typer.Option("scraped_data_v2", "--data-dir", "-d"),
    file_name: str = typer.Option("scraped_articles.json", "--file", "-f"),
):
    """Load data from scraped_articles.json"""
    data_file = Path(data_dir) / file_name

    if not data_file.exists():
        rprint(f"[red]Error: File {data_file} not found![/red]")
        raise typer.Exit(1)

    rprint(f"[yellow]Loading data from {data_file}...[/yellow]")

    db = next(get_db())
    try:
        load_data(db, data_file, ScrapedArticlesLoader)
        rprint("[green]Data loaded successfully![/green]")
    except Exception as e:
        rprint(f"[red]Error loading data: {e}[/red]")
        raise typer.Exit(1)
    finally:
        db.close()


@app.command()
def load_gazzetta_bloggers(
    data_dir: str = typer.Option("scraped_data_v2", "--data-dir", "-d"),
    file_name: str = typer.Option("gazzetta_bloggers_articles.json", "--file", "-f"),
):
    """Load data from gazzetta_bloggers_articles.json"""
    data_file = Path(data_dir) / file_name

    if not data_file.exists():
        rprint(f"[red]Error: File {data_file} not found![/red]")
        raise typer.Exit(1)

    rprint(f"[yellow]Loading data from {data_file}...[/yellow]")

    db = next(get_db())
    try:
        load_data(db, data_file, GazzettaBloggersLoader)
        rprint("[green]Data loaded successfully![/green]")
    except Exception as e:
        rprint(f"[red]Error loading data: {e}[/red]")
        raise typer.Exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    app()
