import datetime
def today():
  td=datetime.datetime.now()
  return f"{td.day}-{td.month}-{td.year}"

def saveFile(filename, data):
  with open(filename,"w") as f:
    f.write(data)
    f.flush()
    f.close()
def readFile(filename):
  with open(filename,"r") as f:
    data=f.read()
    f.close()
    return data