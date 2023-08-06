import numpy as np
import random
import requests
from bs4 import BeautifulSoup


#유의어 크롤링 (다음 사전)
def crawlSynonyms(self, word):
    res = requests.get("https://dic.daum.net/search.do?q="+word+"&dic=kor")
    soup = BeautifulSoup(res.content, "html.parser")
    try:
        link = soup.find("a", class_="txt_cleansch")['href']
    except:
        return []
    link = link[:-19]
    last_link = "https://dic.daum.net"+link+"&q="+word+"&suptype=OPENDIC_KK" # 얻고자하는 단어의 사전 링크

    synonym_list = []
    res = requests.get(last_link)
    soup = BeautifulSoup(res.content, "html.parser")
    try:
        for tag in soup.find("ul", class_="list_learning", id='SIMILAR_WORD').find_all('a'):
            synonym_list.append(tag.text)
    except:
        return []
    if(word in synonym_list):
        synonym_list.remove(word)
    return random.choice(synonym_list)
    
#소프트맥스 함수
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

#question으로 증강된 데이터로 학습한 모델의 예측 출력인 logit을 기존 label로 변경해주는 함수
def logit_to_label(logit, class_n):
    s = 0
    result = []
    for i in range(class_n*2, len(logit)+1, class_n*2):
        t = logit[s:i]
        tmp = []
        for j in range(0, len(t), 2):
            a = softmax([t[j],t[j+1]])
            tmp.append(a[1])
        result.append(np.argmax(tmp))
        s=i
    return result

#question으로 증강된 데이터로 학습한 모델의 예측 확률을 기존 label로 변경해주는 함수
def prob_to_label(prob, class_n):
    s = 0
    result = []
    for i in range(class_n*2, len(prob)+1, class_n*2):
        t = prob[s:i]
        tmp = []
        for j in range(0, len(t), 2):
            tmp.append(t[j+1])
        result.append(np.argmax(tmp))
        s=i
    return result
