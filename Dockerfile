# Install uv
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

FROM python:3.12-slim-bookworm

# Create app user and group with specific UID/GID
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --create-home app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data && \
    chown -R app:app /app && \
    chmod 775 /app && \
    chmod 775 /app/data

WORKDIR /app
USER app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
ENTRYPOINT ["fetch-allocine"]
CMD ["--number_of_pages", "10", "--from_page", "1", \
     "--output_csv_name", "allocine_movies.csv", \
     "--pause_scraping", "2", "10"]