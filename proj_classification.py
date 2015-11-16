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

from wikicrawler import webCrawler
from wikicrawler import Fetcher
from features import features
 
sys.path.append("/Users/gangchen/Downloads/software/pythonlib/scikit-learn-0.15.2/build/lib.macosx-10.7-intel-2.7")
from sklearn import svm
#import sklearn
from sklearn.feature_extraction.text import TfidfTransformer   
from sklearn.externals import joblib

def geturls(url):
    instance = Fetcher(url, "//li")
    urls = instance.extracturl()
    return urls

def getdata(urllists, depth):
    content = []
    nums = []
    nums.append(0)
    for url in urllists:
        #if url != "https://en.wikipedia.org/wiki/1990_RTHK_Top_10_Gold_Songs_Awards":
        #    continue
        crawler = webCrawler(url, depth)
        crawler.crawl()
        nums.append(len(crawler.data))
        content.extend(crawler.data)
    return content    

def buildbow(word_count_threshold, content):
    instance = features(word_count_threshold)    
    word_counts, wordtoix = instance.extractwords(content)
    return word_counts, wordtoix

def processdata(urllists, word_count_threshold, depth):
    content = []
    nums = []
    nums.append(0)
    for url in urllists:
        crawler = webCrawler(url, depth)
        crawler.crawl()
        nums.append(len(crawler.data))
        content.extend(crawler.data)

    instance = features(word_count_threshold)    
    word_counts, wordtoix = instance.extractwords(content)
    N = len(word_counts)
    for i in range(1, len(nums)):
        nums[i] = nums[i-1] + nums[i]
     
    cid = 0   
    output = np.zeros((nums[len(nums)-1], N+1))    
    for url in urllists:
        crawler = webCrawler(url, depth)
        crawler.crawl()
        currlen = len(crawler.data)
        feats = instance.bagofwords(crawler.data, word_counts, wordtoix)
        print feats.shape
        b = np.zeros((currlen,N+1))
        print b[:, :-1].shape
        b[:,0:N] = feats
        b[:,N] = cid +1 
        output[nums[cid]:nums[cid+1],:] = b
        cid = cid + 1
    np.savetxt('test.out', output, delimiter=',')   # X is an array   
    
    
if __name__ == "__main__":
    sys.path.append('/Users/gangchen/Downloads/project/quora/nltk-develop/corpora')
    nltk.data.path[1]= '/Users/gangchen/Downloads/project/quora/nltk-develop'
    word_count_threshold = 0;
    urllists =[]
    urllists.append( "https://en.wikipedia.org/wiki/Category:Rare_diseases");
    urllists.append( "https://en.wikipedia.org/wiki/Category:Infectious_diseases");
    dictname = 'dictionary.txt'
    dict2idx = 'dict2idx.txt'
    filepath = os.path.dirname(os.path.realpath(__file__))
    filename = "test.out"
    if not os.path.isfile(os.path.join(filepath,filename)):
        depth = 1
        # build the dictionary from the corpse
        data =[]
        nums = []
        nums.append(0)
        for url in urllists:
            urls = geturls(url)
            print len(urls)
            #process each class data
            content = getdata(urls, depth)
            data.extend(content)
            nums.append(len(content))
        word_counts, wordtoix = buildbow(word_count_threshold, data)
        
        json.dump(word_counts, file(os.path.join(filepath,dictname), 'w'))
        json.dump(wordtoix, file(os.path.join(filepath,dict2idx), 'w'))
                  
        N = len(word_counts)
    
        # process the length of each class    
        for i in range(1, len(nums)):
            nums[i] = nums[i-1] + nums[i]
     
        cid = 0 # class
        output = np.zeros((nums[len(nums)-1], N+1))    
        for url in urllists:
            urls = geturls(url)
            print urls
            content = getdata(urls, depth)
            instance = features(word_count_threshold) 
            feats = instance.bagofwords(content, word_counts, wordtoix)
            print feats.shape
            currlen = len(content)
            b = np.zeros((currlen,N+1))
            print b[:, :-1].shape
            b[:,0:N] = feats
            b[:,-1] = cid
            output[nums[cid]:nums[cid+1],:] = b
            cid = cid + 1
        np.savetxt(os.path.join(filepath,filename), output, delimiter=',')   # X is an array   

 
    #output = np.loadtxt(os.path.join(filepath,filename), delimiter=',', unpack=True)
    #print output.shape
    #output = output.T
    #output = np.random.permutation(output)
    ##np.random.shuffle
    #print output.shape
    #numdata = len(output)
    #numtrain = int(numdata/2)
    #train_set, test_set = output[numtrain:], output[:numtrain]
    #classifier = nltk.NaiveBayesClassifier.train(train_set)
    ##classifier = nltk.SvmClassifier.train(train_set)
    #acc = nltk.classify.accuracy(classifier, test_set)
    #print acc

        
    output = np.loadtxt(os.path.join(filepath,filename), delimiter=',', unpack=True)
    print output.shape
    output = output.T
    output = np.random.permutation(output)
    #np.random.shuffle
    print output.shape
    numdata = len(output)
    numtrain = int(numdata/2)
    train_set, test_set = output[numtrain:], output[:numtrain]
    X = train_set[:,0:-1]
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    X = tfidf.toarray()
    print X.shape
    y = train_set[:, -1]
    print y
    clf = svm.SVC()
    clf.fit(X, y)
    joblib.dump(clf, 'model.pkl')
    # clf2 = pickle.loads(s)
    tfidf = transformer.fit_transform(test_set[:,0:-1])
    test_X = tfidf.toarray()
    yhat = clf.predict(test_X)
    test_y = test_set[:, -1]
    print yhat
    acc = 0.0;
    for i in xrange(len(test_y)):
        if(yhat[i]==test_y[i]):
            acc = acc+1
    acc = acc/len(test_y)
    print acc
