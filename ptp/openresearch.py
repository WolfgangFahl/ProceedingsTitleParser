'''
Created on 04.07.2020

@author: wf
'''
from wikibot3rd.smw import SMWBot
import os
from wikibot3rd.wikibot import WikiBot
from wikibot3rd.wikiuser import WikiUser
from ptp.event import Event, EventManager


class OpenResearch(object):
    '''
    OpenResearch Semantic Media API
    '''

    def __init__(self,config=None):
        '''
        Constructor
        
        Args:
            config(StorageConfig): the storage configuration to use
        '''
        self.smw=OpenResearch.getSMW()
        self.em=EventManager('or',url='https://www.openresearch.org/wiki/Main_Page',title='OPENRESEARCH',config=config)
        self.debug=self.em.config.debug
        self.profile=self.em.config.profile
        
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
        if self.profile:
            print("retrieving events for openresearch.org cache from SMW")
        while True:
            found,event=self.cacheEventBatch(em,limit=batch,offset=offset)
            if self.profile:
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
            event=self.fromAskResult(askRecord)
            em.add(event)
        found=len(askResult.values())    
        return found,event
        
    def getEvent(self,pageTitle):
        ''' get the event with the given page title (if any) '''
        ask=self.getAsk(pageTitle)      
        askResult=self.smw.query(ask)
        if len(askResult)==1:
            event=self.fromAskResult(next(iter(askResult.values())))
        elif len(askResult)==0:
            event=None
        else:
            raise Exception("%s is ambigous %d result found" % (pageTitle,len(askResult)))        
        return event  
    
    def fromAskResult(self,askRecord):
        ''' 
        initialize the event from the given ask result
        Args:
            askRecord(dict): the SMW ask query record to use as a basis
        Returns:
            even(Event): an event
        '''
        event=Event()
        event.source=self.em.name
     
        d=event.__dict__
        for key in ["event","series","acronym","title","city","homepage","country","start_date","end_date","creation_date","modification_date",'year']:
            if key in askRecord:
                d[key]=askRecord[key]
            else:
                d[key]=None
        ''' individual fixes '''
        if event.series is not None:
            if type(event.series) is list:
                print("warning series for %s is a list: %s - using only 1st entry" % (event.event,event.series))
                event.series=event.series[0]
        if event.country is not None:
            if type(event.country) is list:
                print("warning country for %s is a list: %s" % (event.event,event.country))
            else:
                event.country=event.country.replace("Category:","")  
        if event.start_date is not None:
            event.year=event.start_date.year         
        event.eventId=event.event          
        event.url="https://www.openresearch.org/wiki/%s" % (event.event) 
        event.getLookupAcronym()
        return event

    @staticmethod
    def getSMW():
        wikibot=OpenResearch.getSMW_Wiki()
        smw=SMWBot(wikibot.site)
        return smw
    
    @staticmethod 
    def createWikiUser(wikiId="or"):
        wikiDict={"wikiId": wikiId,"user":"","email":"","url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}   
        wikiUser=WikiUser.ofDict(wikiDict, lenient=True)
        wikiUser.save()
        return wikiUser
    
    @staticmethod    
    def getSMW_Wiki(wikiId="or"):
        iniFile=WikiUser.iniFilePath(wikiId)
        if not os.path.isfile(iniFile):
            wikiUser=OpenResearch.createWikiUser(wikiId)
            wikiUser.save()
            wikibot=WikiBot.ofWikiUser(wikiUser)
        else:    
            wikibot=WikiBot.ofWikiId(wikiId,lenient=True)
        return  wikibot
    
    def initEventManager(self):
        if not self.em.isCached():
            self.cacheEvents(self.em,limit=20000,batch=2000)
            self.em.store()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()
