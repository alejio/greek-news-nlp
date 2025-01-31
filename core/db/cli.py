"""Command-line interface for managing the Gazzetta PostgreSQL database."""

import os
from typing import Optional

import psycopg2
import typer
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from rich import print as rprint

app = typer.Typer(help="Manage Gazzetta PostgreSQL database")


def get_connection(dbname: str = "postgres"):
    """Get a PostgreSQL connection."""
    return psycopg2.connect(
        dbname=dbname,
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
    )


@app.command()
def create(
    dbname: str = "gazzetta",
    force: bool = typer.Option(False, "--force", "-f", help="Drop database if exists"),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="PostgreSQL password"
    ),
):
    """Create the Gazzetta database."""
    if password:
        os.environ["POSTGRES_PASSWORD"] = password
    elif not os.getenv("POSTGRES_PASSWORD"):
        password = typer.prompt("PostgreSQL password", hide_input=True)
        os.environ["POSTGRES_PASSWORD"] = password

    try:
        conn = get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        if force:
            rprint(f"[yellow]Dropping database {dbname} if exists...[/yellow]")
            cur.execute(f"DROP DATABASE IF EXISTS {dbname}")

        rprint(f"[green]Creating database {dbname}...[/green]")
        cur.execute(f"CREATE DATABASE {dbname}")
        rprint(f"[green]Successfully created database {dbname}![/green]")

    except psycopg2.Error as e:
        rprint(f"[red]Database error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


@app.command()
def drop(
    dbname: str = "gazzetta",
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="PostgreSQL password"
    ),
):
    """Drop the Gazzetta database."""
    if password:
        os.environ["POSTGRES_PASSWORD"] = password
    elif not os.getenv("POSTGRES_PASSWORD"):
        password = typer.prompt("PostgreSQL password", hide_input=True)
        os.environ["POSTGRES_PASSWORD"] = password

    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to drop the database '{dbname}'?"
        )
        if not confirm:
            rprint("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()

    try:
        conn = get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        rprint(f"[yellow]Dropping database {dbname}...[/yellow]")
        cur.execute(f"DROP DATABASE IF EXISTS {dbname}")
        rprint(f"[green]Successfully dropped database {dbname}![/green]")

    except psycopg2.Error as e:
        rprint(f"[red]Database error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


@app.command()
def reset(
    dbname: str = "gazzetta",
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="PostgreSQL password"
    ),
):
    """Reset (drop and recreate) the Gazzetta database."""
