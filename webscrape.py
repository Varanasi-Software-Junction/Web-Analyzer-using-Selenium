'''import requests

url = "https://finance.yahoo.com/quote/RELIANCE.NS/history/"
response = requests.get(url)
html_content = response.text
print(html_content)
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from stockslist import stocks
stockname = input("Enter stock name\n")
stockurl = stocks[stockname]
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get("https://finance.yahoo.com/quote/RELIANCE.NS/history/")
driver.get(stockurl)
# Interact with elements, wait for content to load, etc.
page_source = driver.page_source
driver.quit()
print(page_source)
