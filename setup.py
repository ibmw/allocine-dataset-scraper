from pathlib import Path

from setuptools import find_namespace_packages, setup

setup(
    name="allocine_dataset_scraper",
    version="2.2.0",
    description="Scraper for AlloCine",
    author="Olivier Maillot",
    author_email="contact@olivier-maillot.fr",
    url="https://github.com/ibmw/allocine-dataset-scraper",
    install_requires=Path("requirements.txt").read_text().splitlines(),  # dependencies
    packages=find_namespace_packages(include=["allocine_dataset_scraper.*"]),
    include_package_data=False,
    extras_require={"dev": Path("requirements-dev.txt").read_text().splitlines()},
    entry_points={
        "console_scripts": ["fetch-allocine=allocine_dataset_scraper.run:main"],
    },
)
