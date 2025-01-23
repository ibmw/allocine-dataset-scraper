![Test](https://github.com/ibmw/allocine-dataset-scraper/actions/workflows/test.yml/badge.svg?branch=master)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

# 🎬 AlloCine Dataset Scraper

  A Python scraper for collecting movie information from Allociné.fr - the leading French cinema database.

  The script uses http://www.allocine.fr/films webpage to retrieve data as a .csv file saved in data directory.

## 🌟 Features

  - Simple data collection with configurable rate limiting
  - Smart duplicate handling and incremental updates
  - CSV export with automatic directory creation
  - Comprehensive logging with rotation (via loguru)
  - Progress tracking with tqdm
  - Type-safe configuration management (via pydantic)
  - Docker support with non-root user security
  - 90%+ test coverage

## 📊 Data Collection

The scraper collects the following information for each movie:

| Field | Description |
|-------|-------------|
| id | Unique Allocine movie ID |
| title | Movie title (in French) |
| release_date | Release date |
| duration | Movie length |
| genres | Movie genres (up to three) |
| directors | Movie directors |
| actors | Main cast |
| nationality | Movie nationality |
| press_rating | Average press rating (0-5 stars) |
| number_of_press_rating | Number of press ratings |
| user_rating | User ratings (0-5 stars) |
| number_of_spec_rating | Number of user ratings |
| summary | Movie synopsis (in French) |

> 💡 Quick Start: You can [download](https://www.olivier-maillot.fr/wp-content/uploads/2021/10/allocine_movies.csv) a pre-scraped dataset from October 2021 to avoid re-scraping.

## 🚀 Usage

### Prerequisites

- Python 3.12+
- uv (recommended for fast, reliable package management)

### Installation

**As a Python Package**
```bash
# with uv
uv pip install git+https://github.com/ibmw/allocine-dataset-scraper.git

# with pip
pip install git+https://github.com/ibmw/allocine-dataset-scraper.git
```

### Running the Scraper

**CLI Usage**

```bash
# Basic usage with default settings
fetch-allocine

# Check available options
fetch-allocine --help
```

*Available options:*

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| --number_of_pages | INTEGER | Number of pages to scrape | 10 |
| --from_page | INTEGER | First page to scrape | 1 |
| --output_dir | TEXT | Directory for CSV output | data |
| --output_csv_name | TEXT | Output filename | allocine_movies.csv |
| --pause_scraping | INTEGER INTEGER | Range for pause duration (min max) | 2 10 |
| --append_result | FLAG | Append to existing CSV | False |
| --help | FLAG | Show help message and exit | - |

**Python API Usage**

```python
from allocine_dataset_scraper.scraper import AllocineScraper
from allocine_dataset_scraper.config import ScraperConfig

config = ScraperConfig(
    number_of_pages=5,
    from_page=1,
    output_dir="data",
    output_csv_name="movies.csv",
    pause_scraping=(2, 10),
    append_result=False
)

scraper = AllocineScraper(config)
scraper.scraping_movies()
```

**Docker Usage**

```bash
# Pull the latest release
docker pull ghcr.io/ibmw/allocine-dataset-scraper:latest

# Create output directory
mkdir data

# Run the scraper on 10 pages and save the result in allocine_movies.csv file
docker run -v $PWD/data:/app/data:rw ghcr.io/ibmw/allocine-dataset-scraper:latest \
  --number_of_pages 10 \
  --output_csv_name allocine_movies.csv
```

## 🛠️ Development

### Setting Up Development Environment
```bash
# Clone the repository
git clone https://github.com/ibmw/allocine-dataset-scraper.git
cd allocine-dataset-scraper

# Install dependencies with uv
uv sync --all-extras --dev
```
### Quality Checks
```bash
# Run all checks
uv run ruff check .        # Linting
uv run ruff format .       # Formatting
uv run mypy .             # Type checking
uv run pytest --cov       # Tests with coverage
```

### Building Docker Image
```bash
# Build the image
docker build -t allocine_dataset_scraper .
```
## 📝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Run quality checks before committing
4. Commit your changes (git commit -m 'Add some AmazingFeature')
5. Push to the branch (git push origin feature/AmazingFeature)
6. Open a Pull Request

### Development Guidelines
- Maintain test coverage above 90%
- Use type hints consistently
- Follow PEP 8 style guidelines (enforced by ruff)
- Document new functions and classes with docstrings

## 🔒 Security
- Docker image runs as non-root user (UID 1000)
- Rate limiting to respect website's resources
- No sensitive data collection

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Allociné for providing the movie data
- The Python community for the amazing tools and libraries