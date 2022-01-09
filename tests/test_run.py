import pandas as pd
import pytest
from click.testing import CliRunner

from allocine_dataset_scraper.run import cli


@pytest.mark.parametrize(
    "number_of_pages,from_page,pause_start,pause_end,append_result",
    [
        (1, 1, 10, 100, False),
        (1, 10, 0, 1, False),
        (1, 10, 0, 1, True),
    ],
)
def test_run(
    monkeypatch,
    tmp_path,
    get_dataframe,
    number_of_pages,
    from_page,
    pause_start,
    pause_end,
    append_result,
):
    def mock_random(*args):
        return 0

    monkeypatch.setattr(
        "allocine_dataset_scraper.scraper.AllocineScraper._randomize_waiting_time",
        mock_random,
    )
    output_csv_name = "test.csv"
    if append_result:
        path_dir = tmp_path / "data_append"
        path_dir.mkdir()
        full_dir = f"{path_dir}/{output_csv_name}"
        df = get_dataframe
        df.to_csv(full_dir, index=False)
        add_option_list = ["--append_result"]
    else:
        path_dir = tmp_path / "data"
        full_dir = f"{path_dir}/{output_csv_name}"
        add_option_list = []

    output_dir = f"{path_dir}"
    pause_scraping = (pause_start, pause_end)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--number_of_pages",
            number_of_pages,
            "--from_page",
            from_page,
            "--output_dir",
            output_dir,
            "--output_csv_name",
            output_csv_name,
            "--pause_scraping",
            pause_start,
            pause_end,
        ]
        + add_option_list,
    )

    df_scraper = pd.read_csv(full_dir)
    end_shape = df_scraper.shape

    assert f"{number_of_pages=}" in result.output
    assert f"{from_page=}" in result.output
    assert f"{output_dir=}" in result.output
    assert f"{output_csv_name=}" in result.output
    assert f"{pause_scraping=}" in result.output
    assert f"{append_result=}" in result.output
    assert end_shape[1] == 13
    assert end_shape[0] > 0
    assert result.exit_code == 0
    assert not result.exception
