'''
Created on 2020-07-06

@author: wf
'''
import os
import ptp.lookup
import urllib.request
from bs4 import BeautifulSoup
from ptp.event import EventManager, Event

class CEURWS(object):
    '''
    http://ceur-ws.org/ event managing
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        self.em=EventManager("ceur-ws")
        
    def cacheEvents(self):
        ''' test caching the events of CEUR-WS derived from the sample proceeding titles'''
        self.lookup=ptp.lookup.Lookup("CEUR-WS",getAll=False)
        tp=self.lookup.tp
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tc,errs,result=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(result)))
        for title in result:
            if 'acronym' in title.metadata():
                if self.debug:
                    print(title.metadata())
                if 'eventId' in title.info:    
                    event=Event()
                    event.fromTitle(title)
                    event.url="http://ceur-ws.org/%s" % (title.info['eventId'])
                    self.em.add(event)     
        self.em.store()
            
    def initEventManager(self):
        ''' init my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()
        
class CeurwsEvent(object):
    ''' an Event derived from CEUR-WS '''
    
    def __init__(self,debug=False):
        self.debug=debug
        self.title=None
        self.acronym=None
        self.loctime=None
        self.valid=False
        self.err=None
    
    def fromUrl(self,url):
        '''
        construct me from the given url
        '''
        self.proceedingsUrl=url
        self.vol=url.replace("http://ceur-ws.org/","")
        self.vol=self.vol.replace("/","")
        if self.vol:
            self.htmlParse(url)
        
    def htmlParse(self,url):
        # e.g. http://ceur-ws.org/Vol-2635/
        try:
            response = urllib.request.urlopen(url)
    
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")    
                
            self.acronym=self.fromSpan(soup,'CEURVOLACRONYM')
            self.title=self.fromSpan(soup,"CEURFULLTITLE")
            self.loctime=self.fromSpan(soup,"CEURLOCTIME")
            self.valid=True
        except urllib.error.HTTPError as herr:
            self.err=herr
         
    
    def fromSpan(self,soup,spanClass):
        # <span class="CEURVOLACRONYM">DL4KG2020</span>
        # https://stackoverflow.com/a/16248908/1497139
        # find a list of all span elements
        spans = soup.find_all('span', {'class' : spanClass})
        lines = [span.get_text() for span in spans]
        if len(lines)>0:
            return lines[0]
        else:
            return None
            
    def __str__(self):
        ''' convert me to printable text form '''        
        text="%s: %s (%s)" % (self.acronym if self.acronym else '?',
                              self.title if self.title else '?',
                              self.proceedingsUrl)
        return text
        
        