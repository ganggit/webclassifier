1 Overview: 
This project builds a classifer based on bag of words representations. Basically, given a page belonging to certain categories, we first use a simple webpage crawler to get the word frequency, and then we build its histogram representations. Then, we train a simple svm classifier with 50% for training, and the rest 50% for testing.

2. Functionality
wikicrawler.py: to crawler webpages, including content and urls.
features.py: use all pages to build the bag of words representation.
proj_classification: given different page categories, it will learn a svm classifier.

3. Thirdparty toolbox:
NLTK
scikit-learn
lxml

4. test it with >=python 2.7





