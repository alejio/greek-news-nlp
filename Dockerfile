FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ls -la /root/.local/bin && \
    export PATH="/root/.local/bin:$PATH" && \
    uv --version

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY api api/
COPY core core/
COPY data_collection data_collection/
COPY alembic.ini .

# Install project dependencies
ENV PATH="/root/.local/bin:$PATH"
RUN uv sync

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 