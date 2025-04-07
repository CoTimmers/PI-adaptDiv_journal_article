FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (curl is needed to install Poetry)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - && \
    mv /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency files for caching and install dependencies via Poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy the rest of your repository into the container
COPY . .

# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Default command (can be overridden by Docker Compose)
CMD ["bash"]
