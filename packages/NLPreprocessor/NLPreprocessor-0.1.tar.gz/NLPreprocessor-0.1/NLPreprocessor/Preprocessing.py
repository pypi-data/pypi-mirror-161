import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


def remove_unwanted(text):
        import re
        text=str(text)
        text = re.sub(r'https?:\\/\\/.*[\\r\\n]*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\\<a href', ' ', text)
        text = re.sub(r'&amp;', '', text) 
        text = re.sub(r'[_"-\;%()|+&=*%.,!?:#$@\[\]/]', ' ', text)
        text = re.sub(r'<br />', ' ', text)
        text = re.sub(r'\'', ' ', text)
        return(text)

def remove_stopwords(text):
        text=str(text)
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)
        return(text)

def common_words(text):
        text_tokens=word_tokenize(text)
        fdist=FreqDist()
        for word in text_tokens:
            fdist[word.lower()]+=1
        fdist_10=fdist.most_common(10)
        return(fdist_10)

def convert_to_single_string(text):
        single_text=""
        for i in range(len(text)):
            if(i==0):
                single_text=single_text+text[i]
            else:
                single_text=single_text+" "+text[i]
        return(single_text)

def remove_punctuations(text):
        punctuation_remover=RegexpTokenizer(r'\\w+')
        punctuation_remover.tokenize(text)
        return (text)

def lowercase(text):
    
       return(text.lower())

def lemma(text):
        text_tokens=word_tokenize(text)
        word_lem=WordNetLemmatizer()
        #print(text_tokens)
        lemmatized_text=[]
        i=0
        for word in text_tokens:
            lemmatized_text.append(word_lem.lemmatize(word))
            i+=1
        return(lemmatized_text)

def tfidf(X_train,X_test):
    tfidfvectorizer = TfidfVectorizer(use_idf=True,sublinear_tf=True)
    tfidf_train = tfidfvectorizer.fit_transform(X_train)
    tfidf_test  = tfidfvectorizer.transform(X_test)
    return(tfidf_train,tfidf_test)