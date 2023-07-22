# <!--- Imports --->
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag
from requests import Response, get

from log import debug, fatal_error

# <!--- Classes --->
# TODO: Because these types are annoying...
# class Table:
#     headers: List[str] = []
#     values: List[Dict[str, List[Dict[str, str]]]]


class TableBody(List[Dict[str, List[Dict[str, str]]]]):
    pass


# <!--- Functions --->
def download(url: str, file_path: Path | None = None) -> bytes:
    """
    Generic function to download webpages and return their content.

    Optionally, the file_path can be used to set a file to save the request to.
    """
    debug(f"Downloading '{url}'...")
    # Download from remote url
    page: Response = get(url, timeout=5)

    # Make sure the response is valid
    if (page.status_code < 200) or (page.status_code >= 300):
        fatal_error("Invalid status code.")

    # Save to file
    if file_path:
        # Make sure the parent directory exists
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except (FileNotFoundError, OSError):
            fatal_error(f"Failed to create file '{file_path}'!")

        with open(file_path, "wb") as file:
            file.write(page.content)

    # Finally, return the contents of the page
    return page.content


def file_is_outdated(file: Path, days: int = 1) -> bool:
    """
    Checks if a file is outdated and returns either True or False.

    Optionally, the range in days can be used to define how recent a file is.
    Does not account for non-existing files.
    """
    debug(f"Checking recency of '{file}' with range of {days} day(s)...")
    # Get the file's last modified timestamp
    last_modified: float = file.stat(follow_symlinks=True).st_mtime
    file_timestamp: datetime = datetime.fromtimestamp(last_modified)

    # Get maximum date
    maximum_date = datetime.now() + timedelta(-1 * days)

    # Return True if file is too old, otherwise return False
    if file_timestamp <= maximum_date:
        return True
    return False


def get_table(source_html: bytes) -> Tag:
    """
    Parses and returns the table contained in the source_html.
    """
    soup: BeautifulSoup = BeautifulSoup(source_html, "lxml")
    table: Tag | NavigableString | None = soup.find(
        "table", attrs={"border": "1", "align": "center"}
    )

    # Safety checks
    if isinstance(table, NavigableString) or table is None:
        fatal_error("Invalid type returned from parsing html!")
    elif table.tbody is None:
        fatal_error("Table does not contain a valid table body!")

    return table.tbody


def get_items(html_table: Tag) -> Tuple[List[str], TableBody]:
    """
    Parse a BeautifulSoup table Tag and return the table in a workable format.
    """
    headers: List[str] = []
    values: TableBody = TableBody()

    years: List[str] = []

    for row in html_table.find_all("tr", recursive=True):
        for data in row.find_all("td", recursive=True):
            if data.font:
                categorize(data, headers, values, years)
    return (sorted(set(headers), key=headers.index), values)


def categorize(
    tag: Tag,
    headers: List[str],
    # values: List[Dict[str, Dict[str, str]]],
    values: TableBody,
    years: List[str],
) -> None:
    """
    Take a tag, and by using the mutable headers, values and years categorize
    the values contained on the table.

    This is meant to be used together with get_items().
    """
    latest_year: str = years[-1] if len(years) > 0 else ""

    if tag.p and (tag.font is not None and tag.font.strong):
        # Headers
        headers.append(tag.get_text().strip())
    elif not tag.p and tag.font:
        color: str = "\x1b[00m"
        if tag.font.strong:
            # Years
            _year: str = tag.get_text().strip()
            latest_year = _year
            years.append(_year)
        else:
            # Actual Data
            span: str = str(tag.span)

            if r"red" in span:
                color = "\x1b[31m"
            elif r"blue" in span:
                color = "\x1b[34m"

        # Add to values
        if not any(latest_year in item for item in values):
            # Create an empty year
            content: List[Dict[str, str]] = []
            values.append({latest_year: content})
        else:
            # Append to a year
            item: List[Dict[str, str]] = values[-1][latest_year]
            item.append({"value": tag.get_text().strip(), "color": color})
