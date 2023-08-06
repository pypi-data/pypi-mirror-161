import random
import numpy as np
import requests
from bs4 import BeautifulSoup

class Augmentation:
    def __init__(self, mode='whole', tokenizer='okt'):
        assert mode in ['whole','trans','token','no-lib'], "mode must be one of 'whole' or 'trans' or 'token'"
        if mode == 'trans' or mode == 'whole':
            import googletrans
            self.translator = googletrans.Translator()
            self.origin = 'ko'
            
        if mode == 'token' or mode == 'whole':
            from koTextAug.tokenizer import Tokenizer
            self.tokenizer = Tokenizer(tokenizer)
            self.stopwords = ['이', '가', '께서', '에서', '이다', '을', '를', '이', '가', '의', '에', '에서', '에게', '에게서', '한테', '으로', '로', '과', '와', '아', '야', '은', '는', '에선', '라고', '다', '냐', '까']
            self.special = ['.', ',', '!', ';', ':', '\'', '"', '?', '/', '>', '<', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '=']
            self.stopwords.extend(self.special)
        
    def backTranslation(self, sentence, tmp='en'):
        trans = self.translator.translate(sentence, dest=tmp)
        result = self.translator.translate(trans.text, dest=self.origin)
        return result.text

    def backTranslation_list(self, input_list, tmp='en'):
        trans = self.translator.translate(input_list, dest='en')
        trans = [i.text for i in trans]
        result = self.translator.translate(trans, dest=self.origin)
        result = [i.text for i in result]
        return result

    
    def random_swap(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        for _ in range(n):
            i1,i2 = random.sample(range(len(tokens)), 2)
            while (tokens[i1]=='SEP' or tokens[i2]=='SEP' or tokens[i1] in self.stopwords or tokens[i2] in self.stopwords):
                i1,i2 = random.sample(range(len(tokens)), 2)
            tokens[i1], tokens[i2] = tokens[i2], tokens[i1]
        result = self.tokenizer.back_to_sentence(tokens)
        if result==sentence:
            return
        else:
            return result
        
    def random_deletion(self, sentence, p=0.1):
        tokens = self.tokenizer.tokenize(sentence)
        delete = []
        for c in tokens:
            if(c!='SEP' and random.random()<p and c not in self.special):
                delete.append(c)
        if delete==[]:
            return
        for i in delete:
            tokens.remove(i)
        return self.tokenizer.back_to_sentence(tokens)
        
    def crawl_synonyms(self, word):
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

    def synonym_replacement(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        for _ in range (n):
            synonym = []
            cnt = 0
            r = random.choice(tokens)
            while(r == 'SEP' or r in self.stopwords or synonym==[]):
                if(cnt==5): # 유의어가 있는 단어가 없을 경우엔 아무것도 리턴하지 않는다.
                    return 
                cnt+=1
                r = random.choice(tokens)
                synonym = self.crawl_synonyms(r)

            idx = tokens.index(r)
            tokens[idx] = synonym
        return self.tokenizer.back_to_sentence(tokens)
    
    def random_insertion(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        synonym = []
        for _ in range (n):
            cnt = 0
            r = random.choice(tokens)
            while(r == 'SEP' or r in self.stopwords or synonym==[]):
                if(cnt==5): # 유의어가 있는 단어가 없을 경우엔 아무것도 리턴하지 않는다.
                    return 
                cnt+=1
                r = random.choice(tokens)
                synonym = self.crawl_synonyms(r)
            tmp = random.randint(0,len(tokens)-1)
            tokens.insert(tmp, 'SEP' + synonym + 'SEP')
        return self.tokenizer.back_to_sentence(tokens)

    def question(self, info, sent=['긍정','부정'], domain='댓글'):
        comment = info[0]
        label = info[1]
        aug_list = []
        for i,s in enumerate(sent):
            new_label = 1 if i==label else 0
            aug_list.append([comment, '해당 '+domain+'은 '+s+" "+domain+"입니까?", new_label])
        return aug_list 
    
    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    def logit_to_label(self, logit, class_n):
        s = 0
        result = []
        for i in range(class_n*2, len(logit)+1, class_n*2):
            t = logit[s:i]
            tmp = []
            for j in range(0, len(t), 2):
                a = self.softmax([t[j],t[j+1]])
                tmp.append(a[1])
            result.append(np.argmax(tmp))
            s=i
        return result

    def prob_to_label(self, prob, class_n):
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