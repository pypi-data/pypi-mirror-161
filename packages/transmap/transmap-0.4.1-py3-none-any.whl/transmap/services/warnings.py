import requests
from urllib3.exceptions import InsecureRequestWarning


def suppress():
    # Suppress only the single warning from urllib3 needed.
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
