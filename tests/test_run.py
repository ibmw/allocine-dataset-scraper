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

    assert "Starting AlloCine scraper with parameters:" in result.output
    assert f"- Pages to scrape: {number_of_pages} (starting from {from_page})" in result.output
    assert f"- Output: {output_dir}/{output_csv_name}" in result.output
    assert f"- Pause between requests: {pause_scraping[0]}-{pause_scraping[1]}s" in result.output
    assert f"- Mode: {'Append' if append_result else 'Overwrite'}" in result.output
    assert end_shape[1] == 13
    assert end_shape[0] > 0
    assert result.exit_code == 0
    assert not result.exception


def test_run_with_invalid_directory(tmp_path):
    """Test behavior with invalid output directory"""
    runner = CliRunner()
    invalid_dir = "/nonexistent/directory"
    result = runner.invoke(
        cli,
        [
            "--number_of_pages",
            "1",
            "--output_dir",
            invalid_dir,
        ],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_run_with_invalid_pause_values():
    """Test CLI with invalid pause values"""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--number_of_pages",
            "1",
            "--pause_scraping",
            "10",
            "5",  # max < min
        ],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


@pytest.mark.parametrize("pages", [-1, 0, "abc"])
def test_run_with_invalid_page_numbers(pages):
    """Test CLI with invalid page numbers"""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--number_of_pages",
            pages,
        ],
    )
    assert result.exit_code != 0


def test_run_output_file_permissions(tmp_path):
    """Test behavior when output file can't be written"""
    path_dir = tmp_path / "data"
    path_dir.mkdir()
    output_file = path_dir / "test.csv"
    output_file.touch()
    output_file.chmod(0o444)  # Read-only

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--number_of_pages",
            "1",
            "--output_dir",
            str(path_dir),
            "--output_csv_name",
            "test.csv",
        ],
    )
    assert result.exit_code != 0
