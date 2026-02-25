FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==2.1.1

# Configure Poetry: do not create virtualenvs inside the container
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the code
COPY . .

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]