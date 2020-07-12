'''
Created on 2020-07-04

@author: wf
'''
import json
import re
import os
from storage.yamlablemixin import YamlAbleMixin
from storage.jsonablemixin import JsonAbleMixin
import pyparsing as pp

class EventManager(YamlAbleMixin, JsonAbleMixin):
    ''' handle a catalog of events '''
    debug=False
    
    def __init__(self,name,mode='json',withShowProgress=True):
        '''
        Constructor
        '''
        self.name=name
        self.mode=mode
        self.events={}
        self.eventsByAcronym={}
        self.withShowProgress=True
        self.showProgress ("Creating Eventmanager for %s" % (self.name))
        
    def showProgress(self,msg):
        ''' display a progress message '''
        if self.withShowProgress:
            print (msg,flush=True)    
  
    def add(self,event):
        self.events[event.event]=event
        
    def lookup(self,acronym):
        ''' lookup the given event '''
        result=[]
        if acronym in self.events:
            result=[self.events[acronym]]
        elif acronym in self.eventsByAcronym:
            result=self.eventsByAcronym[acronym] 
        return result    
    
    def extractAcronyms(self):
        self.showProgress("extracting acronyms for %s" % (self.name))
        self.eventsByAcronym={}
        grammar= pp.Regex(r'^(([1-9][0-9]?)th\s)?(?P<acronym>[A-Z/_-]{2,10})[ -]*(19|20)[0-9][0-9]$')
        for event in self.events.values():
            if event.acronym is not None:
                try:
                    val=grammar.parseString(event.acronym).asDict()
                    if "acronym" in val:
                        acronym=val['acronym']
                        if acronym in self.eventsByAcronym:
                            self.eventsByAcronym[acronym].append(event)
                        else:
                            self.eventsByAcronym[acronym]=[event]    
                except pp.ParseException as pe:
                    if EventManager.debug:
                        print(event.acronym)
                        print(pe)
                    pass
        self.showProgress ("found %d acronyms" % (len(self.eventsByAcronym)))          
    
    def isCached(self):
        ''' check whether there is a file containing cached 
        data for me '''
        result=os.path.isfile(self.getCacheFile())
        return result
        
    def getCacheFile(self):
        ''' get the path to the file for my cached data '''    
        path=os.path.dirname(__file__)
        cachedir=path+"/../cache"
        cachepath="%s/%s-%s.%s" % (cachedir,self.name,"events",self.mode)
        return cachepath
    
    def fromStore(self):
        cacheFile=self.getCacheFile()
        self.showProgress("reading events from cache %s" % (cacheFile))
        em=None
        if self.mode=="json":   
            em=JsonAbleMixin.readJson(cacheFile)
        else:
            raise Exception("unsupported store mode %s",self.mode)
        if em is not None:
            if em.events is not None:
                self.events=em.events     
        self.showProgress("found %d events" % (len(self.events)))        
        
    def store(self):
        ''' store me '''
        cacheFile=self.getCacheFile()
        self.showProgress ("storing %d events to cache %s" % (len(self.events),cacheFile))
        if self.mode=="json":    
            self.writeJson(cacheFile)
        else:
            raise Exception("unsupported store mode %s",self.mode)    
  
    @staticmethod
    def asWikiSon(eventDicts):  
        wikison=""
        for eventDict in eventDicts:
            wikison+=EventManager.eventDictToWikiSon(eventDict)
        return wikison
    
    @staticmethod
    def eventDictToWikiSon(eventDict):
        wikison="{{Event\n"
        for key,value in eventDict.items():
            if key not in ['foundBy','source','creation_date','modification_date']:
                if value is not None:
                    wikison+="|%s=%s\n" % (key,value)
        wikison+="}}\n"  
        return wikison  
  

class Event(object):
    '''
    an Event
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.foundBy=None
        self.homepage=None
        
    def fromAskResult(self,askRecord):
        ''' initialize me from the given ask result'''
        d=self.__dict__
        for key in ["event","series","acronym","title","city","homepage","country","start_date","end_date","creation_date","modification_date"]:
            if key in askRecord:
                d[key]=askRecord[key]
        ''' individual fixes '''
        if self.country is not None:
            if type(self.country) is list:
                print("warning country for %s is a list: %s" % (self.event,self.country))
            else:
                self.country=self.country.replace("Category:","")     
        self.url="https://www.openresearch.org/wiki/%s" % (self.event) 
        self.fixAcronym()
            
    def fromTitle(self,title):
        ''' fill my data from the given Title '''
        md=title.metadata()
        # fix event field
        if 'event' in md:
            md['eventType']=md['event']
        self.fromDict(md)
        self.fixAcronym()
            
    def fromDict(self,srcDict):
        ''' fill my data from the given source Dict'''
        if 'acronym' in srcDict:
            srcDict['event']=srcDict['acronym']
        d=self.__dict__
        for key in srcDict:
            value=srcDict[key]
            d[key]=value         
    
    def fixAcronym(self):
        if not hasattr(self,'acronym') or self.acronym is None:
            if hasattr(self,'event'):
                self.acronym=self.event
        if hasattr(self,'acronym'):
            if hasattr(self, 'year') and not re.search(r'[0-9]{4}',self.acronym):
                self.acronym="%s %s" % (self.acronym,str(self.year))
            pass       
    
    def asJson(self):
        ''' return me as a JSON record 
        https://stackoverflow.com/a/36142844/1497139 '''
        return json.dumps(self.__dict__,indent=4,sort_keys=True, default=str)
    
    def __str__(self):
        ''' create a string representation of this title '''
        text="%s (%s)" % (self.homepage,self.foundBy)
        return text
