import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'application/json;charset=utf-8'}

def without_kor(text: str) -> str:
    return re.sub('[가-힣]', '', text).strip()

def crawling_element(url: str, element_name: str) -> str:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup.select_one(element_name).text

def crawling_elements(url: str, element_name: str) -> str:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup.select(element_name)

