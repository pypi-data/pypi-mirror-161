import requests
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

PROD_URL = "https://storm-glass-prod.herokuapp.com/marine-weather/v1"
STAGING_URL = "https://storm-glass-staging.herokuapp.com/marine-weather/v1"
DEV_URL = "https://storm-glass-dev.herokuapp.com/marine-weather/v1"
BASEURL = "https://storm-glass-prod.herokuapp.com/marine-weather/v1"
SOFARURL = "https://api.sofarocean.com/marine-weather/v1"

# configure a session with HTTP retries; https://stackoverflow.com/a/35504626
SESSION = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
SESSION.mount("http://", HTTPAdapter(max_retries=retries))
SESSION.mount("https://", HTTPAdapter(max_retries=retries))


def get_token():
    return os.getenv("SOFAR_API_TOKEN", None)


class ExceptionKeyNotFound(Exception):
    pass


def get_url(environment=None):
    if environment:
        if environment == "production":
            if get_token() is None:
                return PROD_URL
            else:
                return SOFARURL
        elif environment == "staging":
            return STAGING_URL
        elif environment == "dev":
            return DEV_URL
    else:
        return BASEURL


def handle_response(response: requests.Response) -> requests.Response:
    if response.status_code == 200:
        return response
    else:
        message = response.content.decode("utf8")
        if "The specified key does not exist" in message:
            raise ExceptionKeyNotFound(f"HTTP response status code {response.status_code} - {message}")
        else:
            raise Exception(f"HTTP response status code {response.status_code} - {message}")


def http_get(endpoint, environment="production"):
    header = {"token": get_token(), "Content-Type": "application/json"}
    tokenstr = f"&token={get_token()}" if get_token() else ""

    url = get_url(environment) + "/" + endpoint + tokenstr
    return handle_response(SESSION.get(url, allow_redirects=True, headers=header))


def set_source(source):
    global BASEURL
    if source == "staging":
        BASEURL = STAGING_URL
    elif source == "production":
        BASEURL = PROD_URL
