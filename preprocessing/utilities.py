## install any dependencies
#pip install emot
#pip install pickle
##https://pypi.org/project/emot/

import ast
import re
import pickle
from emot.emo_unicode import UNICODE_EMOJI
import string

def Convert(string):
    li = ast.literal_eval(string)
    lx = [n.strip() for n in li]
    return lx


def remove_punc(string):
    punc = '''!()[]{};:",-<>/?@$%^&*_~'''
    for ele in string:  
        if ele in punc:  
            string = string.replace(ele, " ") 
    return string  


### use Emoticon_Dict to remove common Emoticons

with open('Emoticon_Dict.p', 'rb') as fp:
    Emoticon_Dict = pickle.load(fp)

def remove_emoticons(text):
    emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in Emoticon_Dict) + u')')
    return emoticon_pattern.sub(r'', text)

### load most common contractions. 

### define functions to remove tokens starting with @, www and create a seperate column for hashtags. 

def strip_all_entities(text):
    entity_prefixes = ['@','#','www.']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)


def save_hashtags(text):
    entity_prefixes = ['#']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] in entity_prefixes:
                words.append(word)
    return words
