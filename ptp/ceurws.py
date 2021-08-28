'''
Created on 2020-07-06

@author: wf
'''
import os
import re
from corpus.datasources.webscrape import WebScrape
from corpus.eventcorpus import EventDataSource, EventDataSourceConfig
from corpus.event import Event, EventSeries, EventManager, EventSeriesManager
from lodstorage.storageconfig import StorageConfig
from ptp.titleparser import TitleParser
from ptp.parsedevent import ParsedEvent

class CeurWs(EventDataSource):
    '''
    http://ceur-ws.org/ event managing
    '''
    sourceConfig = EventDataSourceConfig(
        lookupId="ceurws", 
        name="ceur-ws.org", 
        url='http://ceur-ws.org/',
        title='CEUR Workshop Proceedings',
        tableSuffix="ceurws")

    def __init__(self,debug=False):
        '''
        Constructor
        
        Args:
            config(StorageConfig): the storage configuration to use
        '''
        self.debug=debug
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        super().__init__(CeurWsEventManager(), CeurWsEventSeriesManager(), CeurWs.sourceConfig)
 
    def parseEvents(self,tp:TitleParser):
        '''
        parse the events from the given sample file
        '''
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tc,errs,titles=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(titles)))
        for title in titles:
            if self.debug:
                print(title.metadata())
        return tc,errs,titles
        
    def addParsedTitlesToEventManager(self,titles:list,em:EventManager):
        ''' 
        add the parsed titles of CEUR-WS to the given event manager
        
        Args:
            title(list): the list of titles to add
            em(EventManager): the event manager to use
        '''   
        for title in titles:
            if 'eventId' in title.info:    
                eventId=title.info['eventId']
                event=CeurWsEvent()
                event.fromTitle(title)
                # get the volume as an integer
                try:
                    event.volume=int(re.findall(r'\d+',eventId)[0])
                except Exception as ex:
                    print(f"Warning {ex} for eventId {eventId} title:\n{title}")
                    event.volume=None
                event.url="http://ceur-ws.org/%s" % (eventId)
                em.events.append(event)     
        
    def initEventManager(self):
        ''' init my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()
        
class CeurWsEvent(ParsedEvent):
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
    
def CeurWsEventSeries(EventSeries):
    '''
    CEUR-WS based Event Series
    '''
        
class CeurWsEventManager(EventManager):
    '''
    CEUR-WS  event manager
    '''
        
    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="CeurWsEvents", sourceConfig=CeurWs.sourceConfig, clazz=CeurWsEvent, config=config)
 
class CeurWsEventSeriesManager(EventSeriesManager):
    '''
    CEUR-WS Event Series Manager
    '''
    
    def __init__(self, config: StorageConfig=None):
        '''
        Constructor
        '''
        super().__init__(name="CeurWsEventSeries", sourceConfig=CeurWs.sourceConfig, clazz=CeurWsEventSeries, config=config)
 
    