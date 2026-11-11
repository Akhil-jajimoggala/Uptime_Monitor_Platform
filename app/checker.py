import time
import requests

def read_urls(path="urls.txt"):
    """Return a list of URLs from a file, skipping blank lines."""
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def check_url(url):
    """Check one URL. Return (is_up, status_or_error, seconds)."""
    before_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        elapsed = round(time.perf_counter() - before_time, 3)
        return (True, response.status_code, elapsed)
    
    except requests.exceptions.HTTPError as err:

        elapsed = round(time.perf_counter() - before_time, 3)
        return (False, err.response.status_code, elapsed)

    except requests.exceptions.RequestException as err:
        elapsed = round(time.perf_counter() - before_time, 3)
        return (False, type(err).__name__, elapsed)


def main():
    for url in read_urls():
        is_up, status_code, seconds = check_url(url)
        print("Is Site Up: ", is_up,
              "\nStatus code: ", status_code,
               "\nTime Taken: ",seconds,
               "\nURL: ", url )

if __name__ == "__main__":
    main()