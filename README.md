# Greek News Analysis

A Python package for analyzing Greek sports news articles, focusing on sentiment analysis and stance detection in football coverage.

## Features

- **Data Collection**: Asynchronous scraping of gazzetta.gr articles
- **Stance Analysis**: ML-powered detection of article stance towards teams and referees
- **Database Management**: PostgreSQL storage with Alembic migrations

## Prerequisites

- Python 3.13+
- PostgreSQL
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (for stance analysis)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
uv pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
export POSTGRES_PASSWORD="your_password"
export OPENAI_API_KEY="your_key"
```

## Database Setup

### Initial Setup

Create a new database:
```bash
uv run gazzetta-db create
```

Other database commands:
```bash
# Reset database (drop and recreate)
uv run gazzetta-db reset

# Drop database
uv run gazzetta-db drop
```

### Migrations

We use Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Usage

### Data Collection

Scrape articles from specific bloggers:
```bash
uv run python src/data_collection/scraper_gazzetta_async.py scrape \
    -b "Κώστας Νικολακόπουλος" \
    -o "scraped_data_v2"
```

Options:
- `-b/--blogger`: Target specific blogger(s)
- `-m/--max-articles`: Limit articles per blogger
- `-o/--output-dir`: Output directory
- `-f/--format`: Output format (json, csv)

### Stance Analysis

Analyze article stances towards teams or referees:
```bash
uv run python src/data_collection/nlp/stance_predictor.py analyze \
    --target "Ολυμπιακός" \
    --type "club"
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
ruff check .
```

## License

MIT


