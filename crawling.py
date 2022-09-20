from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import sys

def originalText(nctID):
  # 만약 nctID만 가져왔다면 아래와 같이
  url = "https://www.clinicaltrials.gov/ct2/show/" + nctID
  # 만약 url형식이 들어왔다면
  # url.
  res = requests.get(url)
  soup = BeautifulSoup(res.text, "lxml")

  box = soup.find('div', attrs={"id": "main-content"})
  return box

if __name__ == "__main__":
    # sys.argv[1]은 url임
    print(originalText(str(sys.argv[1])))