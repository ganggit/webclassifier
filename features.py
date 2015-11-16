import pdb
import re, string
import os, sys
import json
from pprint import pprint
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize, word_tokenize

import numpy as np
import scipy as sp

class features(object): 
    
    def __init__(self, word_count_threshold, root=[], locked=True):
        self.root = root
        self.word_count_threshold = word_count_threshold
        self.locked = locked
    
    
    def extractwords(self, data):
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        numdata = 0;
        word_counts = {}
        #pprint(data)
        print len(data)
        for it in data:
        # print line
            line = it['content']
            content = string.join(line)
            #print type(content)
            numdata = numdata + 1
            words = self.preprocess(content) #word_tokenize(line)
            # print words
            for i in range(len(words)):
                word_counts[words[i]] = word_counts.get(words[i],0) + 1
                #word_counts[words[i].lower()] = word_counts.get(words[i].lower(),0) + 1
    
        word_counts = [w for w in word_counts if word_counts[w] >= self.word_count_threshold]
        wordtoix = {}
        ix = 0
        for w in word_counts:
            wordtoix[w] = ix
            ix += 1
        return word_counts, wordtoix
                  
    def bagofwords(self, data, word_counts, wordtoix):
        numdata = len(data)
        features = np.zeros((numdata, len(word_counts)))
        i = 0
        for it in data:
            # print line
            line = it['content']
            content = string.join(line)
            words = self.preprocess(content) #word_tokenize(line)
            gtix = [wordtoix[w] for w in words if w in wordtoix]
            #print gtix
            #print words
            for w in gtix:
                features[i,w] += 1
                #print features[i,:]
                #print features.shape
        i += 1
    
        #sp.io.savemat('bow_features.mat', {'features':features})
        return features
    
                      
    def representations(self):
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        filepath = os.path.dirname(os.path.realpath(__file__))
        filename = 'data.json'
        fname =os.path.join(filepath,filename) #'../test_text.txt'  #'../train.txt-norm'
        numdata = 0;
        word_counts = {}
        #f = open(fname) #open('../train.txt-norm')

        with open(fname) as data_file:    
            data = json.load(data_file)
        #pprint(data)
        for it in data:
        # print line
            line = it['content']
            content = string.join(line)
            #print type(content)
            numdata = numdata + 1
            words = self.preprocess(content) #word_tokenize(line)
            # print words
            for i in range(len(words)):
                word_counts[words[i]] = word_counts.get(words[i],0) + 1
                #word_counts[words[i].lower()] = word_counts.get(words[i].lower(),0) + 1
    
        word_counts = [w for w in word_counts if word_counts[w] >= self.word_count_threshold]
        print len(word_counts)

        wordtoix = {}
        ix = 0
        for w in word_counts:
            wordtoix[w] = ix
            ix += 1

        features = np.zeros((numdata, len(word_counts)))
        i = 0
        for it in data:
            # print line
            line = it['content']
            content = string.join(line)
            words = self.preprocess(content) #word_tokenize(line)
            gtix = [wordtoix[w] for w in words if w in wordtoix]
            #print gtix
            #print words
            for w in gtix:
                features[i,w] += 1
                #print features[i,:]
                print features.shape
        i += 1
    
        #sp.io.savemat('bow_features.mat', {'features':features})
        return features


    def preprocess(self, sentence):
        sentence = sentence.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        #tokenizer = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)
        #sentence = sentence.translate(None, string.punctuation)
        letters = re.sub("[^a-zA-Z]", " ", sentence)
        tokens = tokenizer.tokenize(letters) #tokenizer.tokenize(sentence)
        filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        return filtered_words #" ".join(filtered_words)




if __name__ == "__main__":
    sys.path.append('/Users/gangchen/Downloads/project/quora/nltk-develop/corpora')
    nltk.data.path[1]= '/Users/gangchen/Downloads/project/quora/nltk-develop'
    word_count_threshold = 0;
    instance = features(word_count_threshold)
    feats = instance.representations()
