# backendNodeJS
1. 다음 명령어로 환경 구성
```
npm init
npm install
```
2. secrets.json 최상단에 가져오기
3. config/dev.js 만들기

***
다음 명령어로 서버 실행시키기
```
npm start
```
----------------------------------------------------------
# API 설명
- **개체명 인식기 API** : 약물명 등 다양한 엔티티 감지
	ACM (Amazon Comprehend Medical) API
	AC (Amazon Comprehend) API
	BiolinkBert API
- **의미역 인식기 API** : 약물명과 약물 상세정보 매핑
    ACM (Amazon Comprehend Medical) API

# 자연어처리 모델 학습
자연어처리 모델: BiolinkBert (생의학 자연어처리 모델)
**BiolinkBert** 
- Pre-Training: PubMed 데이터 (21GB)
- Fine-Tuning: ade_corpus_v2 (23516개의 약물명과 약물 부작용 데이터)
- Labeling: 부작용에 관한 문장에서 약물명 위치를 index로 잡아서 라벨링
