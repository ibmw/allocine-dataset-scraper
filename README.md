# AlloCine Dataset Scraper

A scraper to fetch information about movies from Allociné.fr (http://www.allocine.fr/films) - a company which provides information on French cinema.

The script use http://www.allocine.fr/films webpage to retrieve data as a .csv file.

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
### Use as a Python Library

#### from github
- with [pipenv](https://pypi.org/project/pipenv/)
```sh
pipenv install https://github.com/ibmw/allocine-dataset-scraper.git
```
- with pip
```sh
pip install https://github.com/ibmw/allocine-dataset-scraper.git
```
### Developer Mode Installation

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
## Credits
This package was created with Cookiecutter and the [sourcery-ai/python-best-practices-cookiecutter](https://github.com/sourcery-ai/python-best-practices-cookiecutter) project template.
