'''
Created on 2020-08-20

@author: wf
'''
import urllib.request
from bs4 import BeautifulSoup

class WebScrape(object):
    '''
    WebScraper
    with a rudimentary Parser for https://en.wikipedia.org/wiki/RDFa
    extended for CEUR-WS and WikiCFP specific scraping
    
    https://stackoverflow.com/questions/21876602/what-does-the-html-typeof-attribute-do
    https://de.wikipedia.org/wiki/RDFa
    https://stackoverflow.com/questions/20767903/parsing-rdfa-in-html-xhtml
    https://www.w3.org/MarkUp/2009/rdfa-for-html-authors
    '''

    def __init__(self,debug=False,showHtml=False):
        '''
        Constructor
        '''
        self.err=None
        self.valid=False
        self.debug=debug
        self.showHtml=showHtml
        
    def fromSpan(self,soup,spanAttribute,spanValue):
        '''
        get metadata from a given span
        e.g. <span class="CEURVOLACRONYM">DL4KG2020</span>
        '''
        # https://stackoverflow.com/a/16248908/1497139
        # find a list of all span elements
        spans = soup.find_all('span', {spanAttribute : spanValue})
        lines = [span.get_text() for span in spans]
        if len(lines)>0:
            return lines[0]
        else:
            return None
        
    def getSoup(self,url,showHtml):
        '''
        get the beautiful Soup parser 
        '''
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')  
        if showHtml:
            prettyHtml=soup.prettify()
            print(prettyHtml)   
        return soup    
        
    def parseWithScrapeDescription(self,url,scrapeDescr=None):
        '''
        parse the given url with the given encoding
        
        Return:
             a dict with the results
        '''
        try:
            scrapeDict={}
            self.soup=self.getSoup(url, self.showHtml)        
            for scrapeItem in scrapeDescr:
                key=scrapeItem['key']
                value=self.fromSpan(self.soup, scrapeItem['attribute'],scrapeItem['value'])
                scrapeDict[key]=value;  
            self.valid=True
        
        except urllib.error.HTTPError as herr:
            self.err=herr
        return scrapeDict
                
    def parseRDFa(self,url):
        '''
        rudimentary RDFa parsing
        '''
        triples=[]    
        try:
            self.soup=self.getSoup(url, self.showHtml)         
            subjectNodes = self.soup.find_all(True, {'typeof' : True})
            for subjectNode in subjectNodes:
                subject=subjectNode.attrs['typeof']
                if self.debug:
                    print(subjectNode)
                for predicateNode in subjectNode.find_all():
                    value=None 
                    name=None
                    if 'content' in predicateNode.attrs:
                        value=predicateNode.attrs['content']
                    else:
                        value=predicateNode.get_text()    
                    if 'property' in predicateNode.attrs:
                        name=predicateNode.attrs['property'] 
                    if name is not None and value is not None:
                        triples.append((subject,name,value))
            self.valid=True
        except urllib.error.HTTPError as herr:
            self.err=herr
        return triples    
    