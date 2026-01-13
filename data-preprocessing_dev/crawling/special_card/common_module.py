from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import re

def get_driver(chrome_path="chromedriver.exe"):
    service = Service(chrome_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\n', ' ')
    text = re.sub(r'[●▶※■◆!]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()