import time
from pathlib import Path
import requests

URLS_FILE = Path(__file__).parent / "urls.txt"

def read_urls(path = URLS_FILE):
    """Return a list of URLs from a file, skipping blank lines."""
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def check_url(url):
    """Check one URL. Return (is_up, status_or_error, seconds)."""
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        is_up, result = True, response.status_code
    except requests.exceptions.HTTPError as err:
        is_up, result = False, err.response.status_code
    except requests.exceptions.RequestException as err:
        is_up, result = False, type(err).__name__
    return is_up, result, round(time.perf_counter() - start, 3)


def main():
    for url in read_urls():
        is_up, result, seconds = check_url(url)
        state = "UP" if is_up else "DOWN"
        print(f"{state:<5}{result!s:<20}{seconds}s  {url}")


if __name__ == "__main__":
    main()