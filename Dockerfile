FROM python:3.12-slim AS base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Install python dependencies in /.venv
COPY --chmod=777 . .
RUN pipenv install --deploy --system
RUN mkdir -p /home/appuser/data
VOLUME ["/home/appuser/data"]
USER appuser

# Run the executable
ENTRYPOINT ["fetch-allocine"]
CMD ["--number_of_pages", "10", "--from_page", "1", "--output_csv_name", "allocine_movies.csv", "--pause_scraping", "2", "10"]
