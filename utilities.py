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
  