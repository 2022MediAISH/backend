from ast import keyword
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import sys
import re
<<<<<<< HEAD
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')



=======

>>>>>>> fdeae9f53a596f7a02e7b3adba04bac60091adb4
def originalText(keyword):
  # 만약 nctID만 가져왔다면 아래와 같이
  url = keyword
  NCTID = ""
  try:
    NCTID = re.search("NCT[0-9]+", keyword)
    NCTID = NCTID.group()
  except:
    url = keyword.replace(" ", "")
  if("api/query/full_studies" in keyword):
    if(("json" in keyword) or ("JSON" in keyword)):
      response = requests.get(keyword).json()
      NCTID = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["IdentificationModule"]['NCTId']
      # print("This is nctid: "+NCTID)
    # else: xml인 case 도 추가해야됨
  # elif : full_studies 아닌 case 도 추가해야됨

    # NCT ID 추출하기
  if(NCTID != None):
    url = "https://www.clinicaltrials.gov/ct2/show/" + NCTID
  
  
  res = requests.get(url)
  soup = BeautifulSoup(res.text, "lxml")

  box = soup.find('div', attrs={"id": "main-content"})
  return box

if __name__ == "__main__":
    # sys.argv[1]은 url임
    print(originalText(str(sys.argv[1])))