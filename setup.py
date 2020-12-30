from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="allocine_dataset_scraper",
    version="1.0",
    description="Scraper for AlloCine",
    author="Olivier Maillot",
    author_email="contact@olivier-maillot.fr",
    url="https://github.com/ibmw/allocine-dataset-scraper",
    install_requires=Path("requirements.txt").read_text().splitlines(),  # dependencies
    packages=find_packages(),
    include_package_data=False,
    extras_require={"dev": Path("requirements-dev.txt").read_text().splitlines()},
)
