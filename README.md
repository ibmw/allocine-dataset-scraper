  [![Test](https://github.com/ibmw/allocine-dataset-scraper/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/ibmw/allocine-dataset-scraper/actions/workflows/test.yml) [![Weekly Test](https://github.com/ibmw/allocine-dataset-scraper/actions/workflows/auto-test.yml/badge.svg)](https://github.com/ibmw/allocine-dataset-scraper/actions/workflows/auto-test.yml)
  # AlloCine Dataset Scraper

  A scraper to fetch information about movies from Allociné.fr - a company which provides information on French cinema.

  The script uses http://www.allocine.fr/films webpage to retrieve data as a .csv file saved in data directory.

  **Collected Data**

  - `id` : Allocine movie id
  - `title` : Title of the movie (in french)
  - `release_date`: Release date
  - `duration`: Movie length
  - `genres` : Type of movie (up to three different types)
  - `directors` : Movie directors
  - `actors` : Main characters of movie
  - `nationality`: Nationality of the movie
  - `press_rating`: Average of press ratings (from 0 to 5 stars)
  - `number_of_press_rating`: Number of press ratings,
  - `user_rating`:  AlloCiné users ratings (from 0 to 5 stars)
  - `number_of_spec_rating`: Number of users ratings
  - `summary` : Short summary of the movie in french

  > **Note** : You could [download](https://www.olivier-maillot.fr/wp-content/uploads/2021/10/allocine_movies.csv) data scraped in October 2021 to avoid re-scraping all the data.

  ## Getting Started
  ### Installation
  #### Install as a Python Library

  Using [uv](https://github.com/astral-sh/uv) (recommended):

  ```sh
  uv pip install https://github.com/ibmw/allocine-dataset-scraper.git
  ```

  Using pip:

  ```sh
  pip install https://github.com/ibmw/allocine-dataset-scraper.git
  ```

  #### Install As an SDK (Developer Mode)

  Using [uv](https://github.com/astral-sh/uv) (recommended):

  ```sh
  # Clone repo 
  git clone https://github.com/ibmw/allocine-dataset-scraper.git
  cd allocine-dataset-scraper

  # Install dependencies
  uv sync --all-extras --dev
  ```

  Using pip:

  ```sh
  # Clone repo 
  git clone https://github.com/ibmw/allocine-dataset-scraper.git
  cd allocine-dataset-scraper

  # Install dependencies including dev dependencies
  pip install -e ".[dev]"
  ```

  ### Development

  This project uses:
  - [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management
  - [ruff](https://github.com/astral-sh/ruff) for lightning-fast Python linting and formatting
  - [mypy](https://github.com/python/mypy) for static type checking

  To run the quality checks:

  ```sh
  # Run ruff linting
  uv run ruff check .

  # Run ruff formatting
  uv run ruff format .

  # Run type checking
  uv run mypy

  # Run tests with coverage
  uv run pytest --cov
  ```

  ### Usage

  #### CLI 

  Run the fetcher with default values:

  ```sh
  fetch-allocine
  ```

  Check options with --help:

  ```sh
  Usage: fetch-allocine [OPTIONS]

    Simple scraper that retrieve information about movie on AlloCine.fr.

  Options:
    --number_of_pages INTEGER    Number of page to scrape.  [default: 10]
    --from_page INTEGER          First page to scrape.  [default: 1]
    --output_dir TEXT            Directory name to output csv files.  [default:
                                data]
    --output_csv_name TEXT       Output file name (save in a data directory).
                                [default: allocine_movies.csv]
    --pause_scraping INTEGER...  Range to randomize pauses.  [default: 2, 10]
    --append_result              Append result to the output csv file  [default:
                                False]
    --help                       Show this message and exit.
  ```

  #### Inside a script / ipynb:

  ```python
  from allocine_dataset_scraper.scraper import AllocineScraper

  scraper = AllocineScraper(
      number_of_pages=5,
      from_page=1,
      output_dir="data",
      output_csv_name="allocine_movies.csv",
      pause_scraping=[0, 10],
      append_result=False
  )
    
  scraper.scraping_movies()
  ```

  NB: Print out help with `help(scraper)`

  #### With Docker
  ##### Pull mode 

  - **Step 1: Pull the image from [github package](https://github.com/ibmw/allocine-dataset-scraper/pkgs/container/allocine-dataset-scraper)**
  ```sh
  docker pull ghcr.io/ibmw/allocine-dataset-scraper:release
  ```

  - **Step 2: Create a data directory to store the csv file**
  ```sh
  mkdir data
  ```

  - **Step 3: Run the image with arguments**
  ```sh
  docker run -v $PWD/data:/home/app/data:rw allocine_dataset_scraper --number_of_pages 10 --from_page 1 --output_csv_name allocine_movies_dkr.csv --pause_scraping 2 10 
  ```

  *with append_result option*
  ```sh
  docker run -v $PWD/data:/home/app/data:rw allocine_dataset_scraper --number_of_pages 10 --from_page 1 --output_csv_name allocine_movies_dkr.csv --pause_scraping 2 10 --append_result
  ```

  ##### Build mode 

  - **Step 1: Clone the repository**
  ```sh
  git clone https://github.com/ibmw/allocine-dataset-scraper.git
  cd allocine-dataset-scraper
  ```

  - **Step 2: Build the image**
  ```sh
  docker build -t allocine_dataset_scraper .
  ```

  - **Step 3: Create a data directory**
  ```sh
  mkdir data
  ```

  - **Step 4: Run the image with arguments**
  ```sh
  docker run -v $PWD/data:/home/app/data:rw allocine_dataset_scraper --number_of_pages 10 --from_page 1 --output_csv_name allocine_movies_dkr.csv --pause_scraping 2 10 
  ```

  *with append_result option*
  ```sh
  docker run -v $PWD/data:/home/app/data:rw allocine_dataset_scraper --number_of_pages 10 --from_page 1 --output_csv_name allocine_movies_dkr.csv --pause_scraping 2 10 --append_result
  ```