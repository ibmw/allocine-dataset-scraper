# AlloCine Dataset Scraper

A scraper to fetch information about movies from Allociné.fr - a company which provides information on French cinema.

The script use http://www.allocine.fr/films webpage to retrieve data as a .csv file saved in data directory.

**Data Collected**

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
- `summary` : Short summary of the movie

## Getting Start
### Installation
#### Install as a Python Library

- with [pipenv](https://pypi.org/project/pipenv/)

```sh
pipenv install https://github.com/ibmw/allocine-dataset-scraper.git
```

- with pip

```sh
pip install https://github.com/ibmw/allocine-dataset-scraper.git
```

#### Install As an SDK (Developer Mode)

- with [pipenv](https://pypi.org/project/pipenv/)

```sh
# Clone repo 
git clone https://github.com/ibmw/allocine-dataset-scraper.git

# Install dependencies
pipenv install --dev

# Optional : Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
```

- with pip

```sh
# Clone repo 
git clone https://github.com/ibmw/allocine-dataset-scraper.git

pip install -e .[dev]

# Optional : Setup pre-commit and pre-push hooks
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

### Usage

#### CLI 

Run the fetcher with default values : 

- with [pipenv](https://pypi.org/project/pipenv/)
```sh
pipenv run fetch-allocine
```

- with pip
First, you need to activate your environnement.
```sh
fetch-allocine
```

Check options with --help : 

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
  --help                       Show this message and exit.                      
```

#### Inside a script / ipynb :

```python
from allocine_dataset_scraper.scraper import AllocineScraper

scraper = AllocineScraper(number_of_pages=5) 
scraper.scraping_movies()
```

NB : Print out help with `help(scraper)`
