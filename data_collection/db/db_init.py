"""Initialize the database and Alembic migrations."""
import typer
import os
from pathlib import Path
import subprocess
from configparser import ConfigParser

app = typer.Typer()

@app.command()
def init(password: str = typer.Option(..., prompt=True, hide_input=True)):
    """Initialize the database and create initial migration"""
    # Set password in environment
    os.environ["POSTGRES_PASSWORD"] = password
    
    # Create migrations directory if it doesn't exist
    migrations_dir = Path("data_collection/migrations")
    migrations_dir.mkdir(exist_ok=True, parents=True)
    
    # Initialize alembic if not already initialized
    if not (migrations_dir / "env.py").exists():
        subprocess.run(["alembic", "init", "data_collection/migrations"], check=True)
        
    # Update alembic.ini with the correct database URL
    config = ConfigParser()
    config.read('alembic.ini')
    db_url = f"postgresql+psycopg2://postgres:{password}@localhost/gazzetta"
    config.set('alembic', 'sqlalchemy.url', db_url)
    with open('alembic.ini', 'w') as configfile:
        config.write(configfile)
    
    # Create initial migration only if no migrations exist
    versions_dir = migrations_dir / "versions"
    if not list(versions_dir.glob("*.py")):
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
    
    # Run the migration
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    typer.echo("Database initialized successfully!")

if __name__ == "__main__":
    app()