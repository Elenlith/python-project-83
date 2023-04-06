import requests
from bs4 import BeautifulSoup


def get_page_data(url_to_check):
    response = requests.get(url_to_check)
    response.raise_for_status()
    status_code = response.status_code
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.text if soup.h1 else ''
    title = soup.title.text if soup.title else ''
    description = soup.find("meta", attrs={"name": "description"})
    description = description.get("content") if description else ''
    return status_code, h1, title, description
