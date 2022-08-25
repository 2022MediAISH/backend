from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

def originalText(nctID):
  url = "https://www.clinicaltrials.gov/ct2/show/" + nctID
  res = requests.get(url)
  soup = BeautifulSoup(res.text, "lxml")

  box = soup.find('div', attrs={"id": "main-content"})
  return box
