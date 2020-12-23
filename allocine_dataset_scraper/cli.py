from allocine_dataset_scraper import AlloCineScraper

if __name__ == "__main__":

    scraper = AlloCineScraper(
        number_of_pages=int(os.getenv("NUM_PAGES")),
        output_csv_name=os.getenv("DATASET_NAME"),
        human_pause=int(os.getenv("TIMEOUT")),
    )

    scraper.start_scraping_movies()
