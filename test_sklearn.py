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

from scipy.stats import futil
from scipy.sparse.csgraph import _validation

from wikicrawler import webCrawler
from wikicrawler import Fetcher
from features import features
    

sys.path.append("/Users/gangchen/Downloads/software/pythonlib/scikit-learn-0.15.2/build/lib.macosx-10.7-intel-2.7")
from sklearn import svm
#import sklearn
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.externals import joblib    
    
def fsum(data):     
    sumval = 0.0
    for i in xrange(data.shape[1]):
        sumval = sumval + data[:,i]
        #print i
    return sumval    
    
if __name__ == "__main__":
    sys.path.append('/Users/gangchen/Downloads/project/quora/nltk-develop/corpora')
    nltk.data.path[1]= '/Users/gangchen/Downloads/project/quora/nltk-develop'
    word_count_threshold = 0;
    urllists =[]
    urllists.append( "https://en.wikipedia.org/wiki/Sandra_Bullock");
    urllists.append( "https://en.wikipedia.org/wiki/Far_East_scarlet-like_fever");
    filepath = os.path.dirname(os.path.realpath(__file__))
    dictname = 'dictionary.txt'
    dict2idx = 'dict2idx.txt'
    

    with open(os.path.join(filepath,dictname), 'r') as fread:
        word_counts = json.load(fread)
    with open(os.path.join(filepath,dict2idx), 'r') as fread:
        wordtoix = json.load(fread)    
    #np.random.shuffle
    clf = joblib.load('model.pkl')
    for url in urllists:
            crawler = webCrawler(url, 1)
            crawler.crawl()
            instance = features(word_count_threshold) 
            feats = instance.bagofwords(crawler.data, word_counts, wordtoix)
            
            X = feats
            #print X.shape
            print fsum(X)
            transformer = TfidfTransformer()
            tfidf = transformer.fit_transform(X)
            X = tfidf.toarray()
            print fsum(X)
            yhat = clf.predict(X)
            print yhat
            
    print "finish page testing"        
   
