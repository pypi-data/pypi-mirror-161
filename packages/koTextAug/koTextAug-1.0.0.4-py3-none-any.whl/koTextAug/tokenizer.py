class Tokenizer:
    def __init__(self, token):
        if isinstance(token, str):
            option = ['okt','mecab','hannanum','kkma','komoran']
            assert token in option, "Tokenizer must be one of okt or mecab or hannanum or kkma or komoran"
            if token == 'okt':
                from konlpy.tag import Okt
                self.tokenizer = Okt()
            elif token == 'mecab':
                from konlpy.tag import Mecab
                self.tokenizer = Mecab()
            elif token == 'hannanum':
                from konlpy.tag import Hannanum
                self.tokenizer = Hannanum()
            elif token == 'kkma':
                from konlpy.tag import Kkma
                self.tokenizer = Kkma()
            elif token == 'komoran':
                from konlpy.tag import Komoran
                self.tokenizer = Komoran()
        else:
            self.tokenizer = token
            
    def tokenize(self, sentence):
        sentence = sentence.replace(' ', 'SEP')
        tokens = self.tokenizer.morphs(sentence)
        return tokens

    def back_to_sentence(self, tokens):
        return ("".join(tokens).replace('SEP', ' ')).replace("  ", " ")