'''
Created on 2020-07-06

@author: wf
'''
import os
import re
import ptp.lookup
from ptp.webscrape import WebScrape
from ptp.event import EventManager, Event

class CEURWS(object):
    '''
    http://ceur-ws.org/ event managing
    '''

    def __init__(self,config=None):
        '''
        Constructor
        
        Args:
            config(StorageConfig): the storage configuration to use
        '''
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        self.em=EventManager("CEURWS",url='http://ceur-ws.org/',title='CEUR Workshop Proceedings',config=config)
        self.debug=self.em.config.debug
        self.profile=self.em.config.profile
        
    def cacheEvents(self):
        ''' cache the events of CEUR-WS derived from the sample proceeding titles'''
        self.lookup=ptp.lookup.Lookup("CEUR-WS",getAll=False)
        tp=self.lookup.tp
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tc,errs,result=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(result)))
        for title in result:
            if self.debug:
                print(title.metadata())
            if 'eventId' in title.info:    
                event=Event()
                event.fromTitle(title)
                eventId=title.info['eventId']
                # get the volume as an integer
                try:
                    event.volume=int(re.findall(r'\d+',eventId)[0])
                except Exception as ex:
                    print("Warning %s for eventId %s title:\n%s" % (ex,eventId,title))
                    event.volume=None
                event.url="http://ceur-ws.org/%s" % (eventId)
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
        '''
        Constructor 
        '''
        self.debug=debug
        self.title=None
        self.acronym=None
        self.loctime=None
        self.valid=False
        self.err=None
    
    def fromUrl(self,url):
        '''
        construct me from the given url
        
        Args:
           url(string): the url to scrape my info from
        '''
        self.proceedingsUrl=url
        self.vol=url.replace("http://ceur-ws.org/","")
        self.vol=self.vol.replace("/","")
        if self.vol:
            self.htmlParse(url)
        
    def htmlParse(self,url):
        # e.g. http://ceur-ws.org/Vol-2635/
        scrape=WebScrape()
        scrapeDescr=[
            {'key':'acronym', 'tag':'span','attribute':'class', 'value':'CEURVOLACRONYM'},
            {'key':'title',   'tag':'span','attribute':'class', 'value':'CEURFULLTITLE'},
            {'key':'loctime', 'tag':'span','attribute':'class', 'value':'CEURLOCTIME'}
        ]
        scrapedDict=scrape.parseWithScrapeDescription(url,scrapeDescr)
        self.valid=scrape.valid
        self.err=scrape.err
        if self.valid:
            self.acronym=scrapedDict['acronym']
            self.title=scrapedDict['title']
            self.loctime=scrapedDict['loctime']
            
    def __str__(self):
        ''' convert me to printable text form '''        
        text="%s: %s (%s)" % (self.acronym if self.acronym else '?',
                              self.title if self.title else '?',
                              self.proceedingsUrl)
        return text
        
        