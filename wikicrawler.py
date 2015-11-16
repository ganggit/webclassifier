#!/usr/bin/env python

"""Web Crawler/Spider

This module implements a web crawler. This is very _basic_ only
and needs to be extended to do anything usefull with the
traversed pages.
"""

import re, os
import sys, io, json, string
import time
import math
import urllib2
import urlparse
import optparse
from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty

from StringIO import StringIO

sys.path.append("/Users/gangchen/Downloads/software/pythonlib/beautifulsoup4-4.4.1")
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
sys.path.append("/Users/gangchen/Downloads/software/pythonlib/lxml-3.4.4/build/lib.macosx-10.7-intel-2.7")
from lxml import etree
import lxml


__version__ = "0.1"
__license__ = "UB"
__author__ = "Gang Chen"
__author_email__ = "gangchen at buffalo dot edu"

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__

AGENT = "%s/%s" % (__name__, __version__)

class webCrawler(object):

    def __init__(self, url, depth, locked=True):
        self.url = url
        self.depth = depth
        self.locked = locked
        self.host = urlparse.urlparse(url)[1]
        self.urls = []
        self.links = 0
        self.followed = 0
        self.data = []

    def crawl(self):
        page = Fetcher(self.url)
        page.fetch()
        q = Queue()
        for url in page.urls:
            q.put(url)
        followed = [self.url]
        self.data.append({'content':page.content, 'urls':page.urls})
        n = 0
        #print page.urls
        if q.empty():
            return
        while True:
            try:
                url = q.get()
            except QueueEmpty:
                break

            n += 1

            if url not in followed:
                try:
                    host = urlparse.urlparse(url)[1]
                    #print host
                    if self.locked and re.match(".*%s" % self.host, host):
                        followed.append(url)
                        self.followed += 1
                        page = Fetcher(url)
                        page.fetch()
                        purls = []
                        for i, url in enumerate(page):
                            if url not in self.urls:
                                self.links += 1
                                q.put(url)
                                self.urls.append(url)
                                purls.append(url)
                        print page.content
                        self.data.append({'content':page.content, 'urls':purls})
                        #print len(self.data)
                except Exception, e:
                    print "ERROR: Can't process url '%s' (%s)" % (url, e)
                    print format_exc()
                    
            if n >= self.depth and self.depth > 0:
                break         

class Fetcher(object):

    def __init__(self, url, tags='//p'):
        self.url = url # have full path
        self.tags = tags
        # delete the path
        parse_object = urlparse.urlparse(self.url)
        self.root = parse_object.scheme + "://" + parse_object.netloc
        self.urls = []
        self.content = []

    def __getitem__(self, x):
        return self.urls[x]

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def open(self):
        url = self.url
        print url
        try:
            request = urllib2.urlopen(url) #Request(url)
            handle = urllib2.build_opener()
            #url = 'https://www.google.com'
            #doc = lxml.html.fromstring(urllib2.urlopen(url).read())
            
            #parser = etree.HTMLParser()
            #tree = etree.parse(StringIO(request), parser)
        except IOError:
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self.open()
        #self._addHeaders(request)
        if handle:
            try:
                #content = unicode(handle.open(request).read(), "utf-8",
                #        errors="replace")
                #soup = BeautifulSoup(content)
                
                #response = urllib2.urlopen(request)
                outlinks = [];
                the_page = unicode(request.read(), encoding="utf8" , errors="replace")
                doc = lxml.etree.fromstring(the_page)
                raw_html = doc.xpath(self.tags + "/text()")
                content = []
                
                for item in raw_html:
                    try:
                        content.append(item)
                    except AttributeError:
                        print '1'#(item)    
                    #try:
                    #    print(item.text)
                    #except AttributeError:
                    #    print '1'#(item)   
                self.content = content     
                hrefs = doc.xpath(self.tags + "/a")
                
                for href in hrefs:
                    suburl = href.attrib['href']
                    if(suburl.startswith('//')):
                        continue
                    if not suburl.startswith('http'):
                        suburl = self.root + href.attrib['href']  
                    outlinks.append(suburl)
                

                # outlinks.append(self.root + href.attrib['href'])     
 
                #for _, element in etree.iterparse(StringIO(the_page), tag='p'):
                #    print('%s--%s--%s') % (element[0].text, element.find('a'), element[2].text)
                #    print element.text
                #doc = lxml.etree.fromstring(the_page)
                #for x in doc.xpath("//p"):
                #    try:
                #        print(x.text)
                #    except AttributeError:
                #        print(x)
            except etree.XMLSyntaxError: #as e:
                #print (_formatXMLError(e))
                print "XML error"    
            except urllib2.HTTPError, error:
                if error.code == 404:
                    print >> sys.stderr, "ERROR: %s -> %s" % (error, error.url)
                else:
                    print >> sys.stderr, "ERROR: %s" % error
                outlinks = []
            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                outlinks = []
            for href in outlinks:
                if href is not None or href.startswith("http"):
                    url = urlparse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)
                        
                        
    def extracturl(self):
        response = urllib2.urlopen(self.url)
        the_page = unicode(response.read(), encoding="utf-8" , errors="replace")
        doc = lxml.etree.fromstring(the_page)
        hrefs = doc.xpath(self.tags + "/a")
        urls = [];
        for href in hrefs:
            suburl = href.attrib['href']
            if(suburl.startswith('//')):
                continue
            if not suburl.startswith('http'):
                suburl = self.root + href.attrib['href']  
            if suburl not in urls:
                urls.append(suburl)  
        return urls                           
'''
def getLinks(url):
    page = Fetcher(url)
    page.fetch()
    for i, url in enumerate(page):
        print "%d. %s" % (i, url)
'''
    
def getLinks(url, urlroot='https://en.wikipedia.org'):
    response = urllib2.urlopen(url)
    the_page = unicode(response.read(), encoding="utf-8" , errors="replace")
    doc = lxml.etree.fromstring(the_page)
    hrefs = doc.xpath('//a')
    links = [];
    for href in hrefs:
        suburl = href.attrib['href']
        if not suburl.startswith('http'):
            suburl = urlroot + href.attrib['href']  
        if suburl not in links:
            links.append(suburl)  
    return links                 
    
def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-q", "--quiet",
            action="store_true", default=False, dest="quiet",
            help="Enable quiet mode")

    parser.add_option("-l", "--links",
            action="store_true", default=False, dest="links",
            help="Get links for specified url only")

    parser.add_option("-d", "--depth",
            action="store", type="int", default=20, dest="depth",
            help="Maximum depth to traverse")

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

def main():
    opts, args = parse_options()

    url = args[0]

    if opts.links:
        getLinks(url)
        raise SystemExit, 0

    depth = opts.depth

    sTime = time.time()

    print "Crawling %s (Max Depth: %d)" % (url, depth)
    crawler = webCrawler(url, depth)
    crawler.crawl()
    #print "\n".join(crawler.urls)

    eTime = time.time()
    tTime = eTime - sTime

    print "Found:    %d" % crawler.links
    print "Followed: %d" % crawler.followed
    print "Stats:    (%d/s after %0.2fs)" % (
            int(math.ceil(float(crawler.links) / tTime)), tTime)
    
    filename = "data.json"
    filepath = os.path.dirname(os.path.realpath(__file__))
    with io.open(os.path.join(filepath,filename), 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(crawler.data, ensure_ascii=False)))
    
if __name__ == "__main__":
    main()
