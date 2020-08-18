'''
Created on 04.07.2020

@author: wf
'''
from wikibot.smw import SMW
import os
from wikibot.wikibot import WikiBot
from ptp.event import Event, EventManager


class OpenResearch(object):
    '''
    OpenResearch Semantic Media API
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.smw=OpenResearch.getSMW()
        self.debug=debug
        self.em=EventManager('or',url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH',debug=self.debug)
        
    def getAsk(self,condition,limit=50,offset=0):    
        ask="""{{#ask: [[%s]]
| mainlabel=event
| ?Acronym = acronym
| ?Title = title
| ?Event in series = series
| ?Homepage = homepage
| ?Has location city = city
| ?Has_location_country = country
| ?End_date = end_date
| ?Start_date = start_date
| ?_CDAT = creation_date
| ?_MDAT = modification_date
| limit = %d
| offset = %d
}}
""" % (condition,limit,offset)
        return ask

    def cacheEvents(self,em,limit=500,batch=5000):
        offset=0
        if self.debug:
            print("retrieving events for openresearch.org cache")
        while True:
            found,event=self.cacheEventBatch(em,limit=batch,offset=offset)
            if self.debug:
                em.showProgress("retrieved events %5d-%5d" % (offset+1,offset+found))
                em.showProgress(event.asJson())
            offset=offset+batch
            if found<batch or len(em.events)>=limit:
                break
     
        return em
     
    def cacheEventBatch(self,em,limit=500,offset=0):
        ''' get an eventmanager for caching events '''
        ask=self.getAsk("isA::Event",limit=limit,offset=offset)
        askResult=self.smw.query(ask)
        event=None
        for askRecord in askResult.values():
            event=Event()
            event.fromAskResult(askRecord)
            event.source=self.em.name
            em.add(event)
        found=len(askResult.values())    
        return found,event
        
    def getEvent(self,pageTitle):
        ''' get the event with the given page title (if any) '''
        ask=self.getAsk(pageTitle)      
        askResult=self.smw.query(ask)
        if len(askResult)==1:
            event=Event()
            event.fromAskResult(next(iter(askResult.values())))
        elif len(askResult)==0:
            event=None
        else:
            raise Exception("%s is ambigous %d result found" % (pageTitle,len(askResult)))        
        return event  

    @staticmethod
    def getSMW():
        wikibot=OpenResearch.getSMW_Wiki()
        smw=SMW(wikibot.site)
        return smw
        
    @staticmethod    
    def getSMW_Wiki():
        wikiId="or"
        iniFile=WikiBot.iniFilePath(wikiId)
        if not os.path.isfile(iniFile):
            WikiBot.writeIni(wikiId,"OpenResearch.org","https://www.openresearch.org","/mediawiki/","MediaWiki 1.31.1")    
        wikibot=WikiBot.ofWikiId(wikiId)
        return  wikibot
    
    def initEventManager(self):
        if not self.em.isCached():
            self.cacheEvents(self.em,limit=20000,batch=2000)
            self.em.store()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()
