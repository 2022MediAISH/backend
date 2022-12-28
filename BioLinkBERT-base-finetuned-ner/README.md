---
license: apache-2.0
tags:
- generated_from_trainer
metrics:
- precision
- recall
- f1
- accuracy
model-index:
- name: BioLinkBERT-base-finetuned-ner
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# BioLinkBERT-base-finetuned-ner

This model is a fine-tuned version of [michiyasunaga/BioLinkBERT-base](https://huggingface.co/michiyasunaga/BioLinkBERT-base) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 0.1226
- Precision: 0.8760
- Recall: 0.9185
- F1: 0.8968
- Accuracy: 0.9647

## Model description

This model is designed to perform NER function for specific text using BioLink BERT

## Intended uses & limitations

The goal was to have a drug tag printed immediately for a particular sentence, but it has the disadvantage of being marked as LABEL

LABEL0 : irrelevant text
LABEL1,2 : Drug
LABEL3,4 : condition

## Training and evaluation data

More information needed

## Training procedure

Reference Code: SciBERT Fine-Tuning on Drug/ADE Corpus (https://github.com/jsylee/personal-projects/blob/master/Hugging%20Face%20ADR%20Fine-Tuning/SciBERT%20ADR%20Fine-Tuning.ipynb) 

## How to use

from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("HMHMlee/BioLinkBERT-base-finetuned-ner")

model = AutoModelForTokenClassification.from_pretrained("HMHMlee/BioLinkBERT-base-finetuned-ner")

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 1e-05
- train_batch_size: 16
- eval_batch_size: 16
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 5

### Training results

| Training Loss | Epoch | Step | Validation Loss | Precision | Recall | F1     | Accuracy |
|:-------------:|:-----:|:----:|:---------------:|:---------:|:------:|:------:|:--------:|
| 0.1099        | 1.0   | 201  | 0.1489          | 0.8415    | 0.9032 | 0.8713 | 0.9566   |
| 0.1716        | 2.0   | 402  | 0.1318          | 0.8456    | 0.9135 | 0.8782 | 0.9597   |
| 0.1068        | 3.0   | 603  | 0.1197          | 0.8682    | 0.9110 | 0.8891 | 0.9641   |
| 0.0161        | 4.0   | 804  | 0.1219          | 0.8694    | 0.9157 | 0.8919 | 0.9639   |
| 0.1499        | 5.0   | 1005 | 0.1226          | 0.8760    | 0.9185 | 0.8968 | 0.9647   |


### Framework versions

- Transformers 4.20.1
- Pytorch 1.12.0+cu113
- Datasets 2.4.0
- Tokenizers 0.12.1


---
## 자연어처리 모델 학습
자연어처리 모델: BiolinkBert (생의학 자연어처리 모델)
**BiolinkBert** 
- Pre-Training: PubMed 데이터 (21GB)
- Fine-Tuning: ade_corpus_v2 (23516개의 약물명과 약물 부작용 데이터)
- Labeling: 부작용에 관한 문장에서 약물명 위치를 index로 잡아서 라벨링

## 1) Hugging Face 로그인
## 2) 모델 불러오기
```
tokenizer = AutoTokenizer.from_pretrained("BioLinkBERT-base-finetuned-ner",model_max_length=512)
model = AutoModelForTokenClassification.from_pretrained("BioLinkBERT-base-finetuned-ner")
effect_ner_model = pipeline(task="ner", model=model, tokenizer=tokenizer, device=-1)
```
## 3) 모델 구조
각 토큰별 LABEL_# 를 리턴받음

- LABEL_0 : 'O' (해당 없음)
- LABEL_1 : 'B-DRUG' (토큰화된 약물명의 첫번째 토큰)
- LABEL_2 : 'I-DRUG' (토큰화된 약물명의 첫번째를 제외한 토큰)
- LABEL_3 : 'B-EFFECT' (사용안함)
- LABEL_4 : 'I-EFFECT' (사용안함)

**약물을 감지했을때 API 형태**
```
[
  {'entity': 'LABEL_1', 'score': 0.98608416, 'index': 1, 'word': 'pr', 'start': 0, 'end': 2}, {'entity': 'LABEL_2', 'score': 0.98828495, 'index': 2, 'word': '##uc',    'start': 2, 'end': 4}, 
  {'entity': 'LABEL_2', 'score': 0.987498, 'index': 3, 'word': '##alo', 'start': 4, 'end': 7}, {'entity': 'LABEL_2', 'score': 0.9862112, 'index': 4, 'word': '##pri', 'start': 7, 'end': 10}, {'entity': 'LABEL_2', 'score': 0.98280567, 'index': 5, 'word': '##de', 'start': 10, 'end': 12}
]
```

**Token Combine 방법**

```
def visualize_entities(sentence):
    tokens = effect_ner_model(sentence)
    label_list = ['O', 'B-DRUG', 'I-DRUG', 'B-EFFECT', 'I-EFFECT']
    entities = []
    last = 0
    i = 0

    for token in tokens:
        label = int(token["entity"][-1])
        if label == 1 or label == 2:  //해당 토큰의 LABEL이 LABEL_1, LABEL_2일때는 약물명에 대한 토큰이기에, 이를 합치는 과정을 진행함
            token["label"] = label_list[label]
            entities.append(token["word"])
    while(last != len(entities) and last != -1):
      for i in range(last, len(entities)):
        if entities[i][0] == '#': // 토큰에 붙어 있는 #을 지우는 과정
          entities[i - 1] = entities[i - 1] + entities[i][2:]
          entities.pop(i)
          last = i
          break
        elif i == len(entities) - 1 :
          last = -1
    
    return entities
```

Token Combine 결과: prucalopride
