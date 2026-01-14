from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from stockslist import stocks
import utilities as ut

stockname = input("Enter stock name\n").strip().lower()
stockurl = stocks.get(stockname)

if not stockurl:
    print(f"{stockname} not found")
    exit()

search = stockurl.strip().split("/")[-1]
print("Loading:", stockurl)

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)

try:
    driver.get(stockurl)

    WebDriverWait(driver, 20).until(
        lambda d: search in d.page_source
    )
    price_el = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="qsp-price"]'))
    )

    page_source = driver.page_source  # <-- BEFORE quit
    print("Price:", price_el.text)

    page_source = driver.page_source
    filename=ut.getNewFileName(stockname)
    ut.saveFile(filename, page_source)

    # print("Page saved successfully")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()
