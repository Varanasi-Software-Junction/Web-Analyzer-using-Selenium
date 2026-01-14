import datetime
def today():
  td=datetime.datetime.now()
  return f"{td.day}-{td.month}-{td.year}"

def getNewFileName(stockname):
  return f"{stockname}_{today()}.html"
def saveFile(filename, data):
  with open(filename, "w", encoding="utf-8", errors="replace") as f:
    f.write(data)

 
    f.flush()
    f.close()
def readFile(filename):
  with open(filename,"r") as f:
    data=f.read()
    f.close()
    return data
  
def getStockPrice(stockname):
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC

  from stockslist import stocks
  stockurl = stocks.get(stockname)

  if not stockurl:
      print(f"{stockname} not found")
      return None

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
      # print("Price:", price_el.text)

      page_source = driver.page_source
      filename=getNewFileName(stockname)
      saveFile(filename, page_source)

      return float(price_el.text.replace(",","")),filename

  except Exception as e:
      # print("Error:", e)
      return e

  finally:
      driver.quit()
       


