from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from stockslist import stocks
import utilities as ut


stockname = input("Enter stock name\n").strip()
stockurl = stocks.get(stockname, 0)
print(stockurl)
if stockurl == 0:
    print(f"{stockname} not found")
else:
    stockurl=stockurl.strip()

    search = stockurl.split("/")[-1]
    # search=f"{search.strip()}".strip()
    print(search, stockurl)

    driver = webdriver.Chrome()
    driver.get(stockurl)

    WebDriverWait(driver, 20).until(
        lambda d: search in d.page_source)
    # WebDriverWait(driver, 20).until(
    # lambda d: "₹" in d.page_source)

    driver.quit()

    page_source = driver.page_source
    print(page_source)
    ut.saveFile(f"{stockname}{ut.today()}.txt", page_source)
