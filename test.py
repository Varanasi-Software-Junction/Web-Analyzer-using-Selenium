from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import stockslist as st
import utilities as ut

driver = webdriver.Chrome()
stockname=input("Enter stock name\n").strip()
# stockurl="https://finance.yahoo.com/quote/RELIANCE.NS"
stockurl=st.stocks.get(stockname)
driver.get(stockurl)
search=stockurl.split("/")[-1]

WebDriverWait(driver, 20).until(
    lambda d: search in d.page_source
)
print("Found")
# WebDriverWait(driver, 20).until(
#     lambda d: "₹" in d.page_source
# )
 
print("Reliance Share Price:", driver.page_source)
ut.saveFile("hello",driver.page_source)

driver.quit()
# ut.saveFile(stockname,driver.page_source)
