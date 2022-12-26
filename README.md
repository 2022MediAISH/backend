# 임상시험 설계 모식도 자동생성 및 시각화_Backend
> 입력받은 글로벌 임상시험(ClinicalTrials.gov) URL에서 PICOT 기반의 의미있는 정보를 추출하여 이를 모식도로 시각화하는 웹 어플리케이션입니다.    
추출된 정보가 정확한지 확인할 수 있도록 글로벌 임상시험 URL의 원문을 함께 보여주며, 내용 혹은 모식도의 모양을 수정할 수 있는 기능을 제공합니다. 모식도의 글자를 클릭하면 해당 내용이 적힌 원문으로 이동하고, 최근에 검색했던 모식도 기록을 보여주는 기능 또한 제공합니다.

## Getting Started
### Clone Repository
```
$ git clone https://github.com/2022MediAISH/backend.git
$ cd backend
```
### How to Run
#### 1. Installation:
```
$ npm init
$ npm install
$ python -m pip install -U pip
$ pip install -r requirements.txt
```
#### 2. secrets.json 최상단에 가져오기    
해당 파일 안에는 다음의 내용들이 있다.
- AWS의 access_key_id
- AWS의 secret_access_key
- AWS의 region_name
- mongodb의 collection이름과 비밀번호, 연결 주소와 포트번호 등의 정보가 담긴 URL
```
{
  "aws_access_key_id" : "(access key id)",
  "aws_secret_access_key" : "(secret access key)",
  "region_name" : "(region name)",
  "mongoURI": "mongodb://(collectionName):(password)@(connect IP):(connect PORT)/?authMechanism=DEFAULT&authSource=admin"
}

```
#### 3. config/dev.js 만들기
해당 파일 안에는 다음의 내용이 있다.
- mongodb의 collection이름과 비밀번호, 연결 주소와 포트번호 등의 정보가 담긴 URL
```
module.exports = {
  mongoURI:
    "mongodb://(collectionName):(password)@(connect IP):(connect PORT)/?authMechanism=DEFAULT&authSource=admin",
};
```

#### 4. To run Express
```
npm start
```

## 파일 구조
```
.
├── BioLinkBERT-base-finetuned-ner/
├── config/
|   ├── dev.js
|   ├── key.js
|   ├── prod.js
├── NCT_ID_database_acm/
|   └── ...
├── NCT_ID_database_bio
|   └── ...
├── .gitignore
├── crawling.py
├── data_extract_ACM.py
├── data_extract_Biolinkbert.py
├── img-nct.txt
├── img-url.txt
├── index.js
├── modules.txt
└── secrets.json
```
- config/ : MongoDB를 사용하는데 필요한 정보를 저장
- NCT_ID_database_acm/ :data_extract_ACM.py를 실행해 추출된 정보를 저장
- NCT_ID_database_bio/ : data_extract_Biolinkbert.py를 실행해 추출된 정보를 저장
- crawling.py : ClinicalTrials의 임상시험 원문을 가져옴
- data_extract_ACM.py : ACM api와 ClinicalTrials api로 정보를 추출, json형태로 내보냄
- data_extract_Biolinkbert.py : ACM api와 ClinicalTrials api와 Biolinkbert api로 정보를 추출, json형태로 내보냄
- img-url.txt와 img-nct.txt: 모식도 생성시 만들어지는 모식도 이미지와 임상시험번호 기록
- index.js : 모든 API
- modules.txt : 정보추출 코드를 실행시키는 데 필요한 모듈들
- secrets.json : AWS 사용에 필요한, 노출되면 안 되는 값들을 저장
----------------------------------------------------------
## API Call 
url = http://3.35.243.113:5000
 
### 1) url + '/api’ [POST]
전달받은 임상시험설계 url에서 임상시험번호(NCTID)를 추출하고, 이를 이용해 ClinicalTrials api에 접근
#### Request 예시
```
{ url: (ClinicalTrials.gov의 임상시험설계번호) }
```
#### Response 예시
```
{
    "Allocation": "(Allocation 방법)",
    "CompleteTime": (연구 총 수행기간),
    "DesignModel": "(interventional 임상시험의 type)",
    "DrugInformation": {
        "ArmGroupList": [
            {
                "ArmGroupDescription": "(중재군 설명)",
                "ArmGroupLabel": "(중재군 이름)",
                "ArmGroupType": "(중재군 종류)",
                "InterventionDescription": [
                    {
                        "Dosage": "(약물 복용량)",
                        "DrugName": "(약물 이름)",
                        "Duration": "(약물 투여기간)",
                        "HowToTake": "(약물 섭취방법)",
                        "OtherName": [(약물의 다른 이름)]
                    }
                ],
                "InterventionList": {
                    "ArmGroupInterventionName": [
                        "(중재군에서 사용하는 약물이름)",
                        …
                    ]
                }
            },
            …
        ]
    },
    "Enrollment": "(모집된 피험자 수)",
    "InterventionName": "(사용된 약물 이름)",
    "Masking": "(Masking 방법)",
    "NCTID": "(임상시험설계번호)",
    "Objective": "(임상시험 목적)",
    "OfficialTitle": "(임상시험설계 이름)",
    "PopulationBox": {
        "Condition": "(임상시험에서 다루는 병/상태)",
        "Gender": "(성별)",
        "HealthyCondition": "(건강한 사람 모집 여부)",
        "MaxAge": "(모집하는 피험자의 최대 나이)",
        "MinAge": "(모집하는 피험자의 최소 나이)",
        "Participant": "(모집된 피험자 수)"
    },
    "PopulationRatio": "(중재군 별 비율)",
    "Title": "(임상시험설계 제목)",
    "WashoutPeriod": "(휴약기간)",
    "_id": "(임상시험설계번호)",
    "version": "(정보추출API의 버전)"
}
```
### 2) url + '/load’ [POST]
전달받은 임상시험설계번호(NCTID)로 편집본을 저장하고 있는 데이터베이스 검색함
존재한다면 데이터베이스에서 원본 정보(json)를 반환하고, 
없다면 아무일도 하지 않음
#### Request 예시
```
{url: (ClinicalTrials.gov의 임상시험설계번호)}
```
#### Response 예시 
```
‘/api’의 Response예시와 유사. 원본 내용을 담고 있음
```
### 3) url + '/create' [POST]
처음 추출된 데이터를 저장하고 있는 폴더에 접근하여, 전달받은 임상시험설계번호(NCTID)로 편집하고자 하는 json파일을 open하고 수정
편집된 내용을 데이터베이스에 삽입
#### Request 예시
```
‘/api’의 Response예시와 유사. 다만, 편집된 내용을 담고 있음
```
#### Response 예시 
```
‘/api’의 Response예시와 유사. 편집된 내용을 담고 있음
```
### 4) url + '/img' [POST]
생성된 모식도의 이미지의 경로와 임상시험번호를 텍스트 형태로 저장
#### Request 예시
```
{ (생성된 모식도 이미지의 경로), (임상시험설계번호) }
```
#### Response 예시 
```
{ “message”: “Good” }
```
### 5) url + `/crawling`, body [POST]
임상시험 원문 내용 태그들을 추출하여 전달

#### Request 예시
```
{url: (ClinicalTrials.gov의 임상시험설계번호)}
```
#### Response 예시
```
(크롤링된 태그들이 전달됨)
```
### 6) url + '/img' [GET]
텍스트 형태로 저장된 이미지와 임상시험설계번호에서 최근 3개를 클라이언트에게 반환
##### Response 예시 
```
{ (생성된 모식도 이미지의 경로), (임상시험설계번호) }
```

### 사용하는 API 추가 설명
- **개체명 인식기 API** : 약물명 등 다양한 엔티티 감지
	ACM (Amazon Comprehend Medical) API
	AC (Amazon Comprehend) API
	BiolinkBert API
- **의미역 인식기 API** : 약물명과 약물 상세정보 매핑
    ACM (Amazon Comprehend Medical) API

## 자연어처리 모델 학습
자연어처리 모델: BiolinkBert (생의학 자연어처리 모델)
**BiolinkBert** 
- Pre-Training: PubMed 데이터 (21GB)
- Fine-Tuning: ade_corpus_v2 (23516개의 약물명과 약물 부작용 데이터)
- Labeling: 부작용에 관한 문장에서 약물명 위치를 index로 잡아서 라벨링
