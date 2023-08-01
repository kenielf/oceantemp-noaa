# <!--- Imports --->
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import List, Tuple

from bs4 import Tag

from data.scraper import TableBody, download, file_is_outdated, get_items, get_table
from log import debug, error, info

# <!--- Constants --->
REMOTE_SOURCE: str = (
    "https://origin.cpc.ncep.noaa.gov/products/"
    "analysis_monitoring/ensostuff/ONI_v5.php"
)

INSTANCE_DIR: Path = Path(__file__).parent.parent / "instance"


# <!--- Functions --->
def extract_data() -> Tuple[List[str], TableBody]:
    """
    Extract the data from local or remote sources and return a formatted json
    file.
    """
    info("Extracting data...")

    source_html_file: Path = INSTANCE_DIR / "noaa-oni.html"
    data_file: Path = INSTANCE_DIR / "data.json"

    # Check if the data already exists and is up to date.
    if (not data_file.exists()) or file_is_outdated(data_file):
        debug("Data file does not exist, downloading...")
        # See if the downloaded remote source is usable
        return download_and_parse(source_html_file, data_file)

    # Read from file
    debug("Reading from file...")
    with open(data_file, "r") as file:
        try:
            return loads(file.read())
        except JSONDecodeError:
            return download_and_parse(source_html_file, data_file)


def download_and_parse(html_file: Path, _df: Path) -> Tuple[List[str], TableBody]:
    if not html_file.exists():
        html: bytes = download(REMOTE_SOURCE, html_file)
    else:
        debug("HTML file is up to date, reading...")
        with open(html_file, "rb") as file:
            html = file.read()

    # Parse to file
    with open(_df, "w") as file:
        table: Tuple[List[str], TableBody] = parse_data(html)
        file.write(dumps(table, sort_keys=True, indent=2))
        return table


def parse_data(html_source: bytes) -> Tuple[List[str], TableBody]:
    """
    Take a html page and parse it into a usable data table.
    """
    info("Parsing Data...")
    table: Tag = get_table(html_source)

    return get_items(table)


def print_table(headers: List[str], values: TableBody) -> None:
    """
    Prints a table, usually acquired by loading a file or
    """
    VSEP: str = "|"
    DATA_SIZE: int = 7
    YEAR_SIZE: int = 6
    # The length of the separator is the sum of the sizes of each column,
    # summed with the amount of separators
    SEP_LEN: int = (YEAR_SIZE) + (12 * DATA_SIZE) + (13)
    # SEP_LEN: int = ((YEAR_SIZE) + (12 * DATA_SIZE)) + (YEAR_SIZE + DATA_SIZE)
    # Headers
    print(f"{headers[0]:^{YEAR_SIZE}}{VSEP}", end="")
    for i in headers[1::]:
        print(f"{i:^{DATA_SIZE}}", end=VSEP)
    print()
    # Separator
    print("-" * SEP_LEN)
    # Values
    for _dict in values:
        for key, value in _dict.items():
            print(f"\x1b[33m{key}", end=f":\x1b[00m {VSEP}")
            for i in value:
                print(f"{i['color']}{i['value']:^{DATA_SIZE}}\x1b[00m", end=VSEP)
            print()
