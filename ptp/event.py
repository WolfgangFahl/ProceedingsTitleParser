'''
Created on 04.07.2020

@author: wf
'''
import json
import os
from storage.yamlablemixin import YamlAbleMixin
from storage.jsonablemixin import JsonAbleMixin
import pyparsing as pp

class EventManager(YamlAbleMixin, JsonAbleMixin):
    ''' handle a catalog of events '''
    debug=False
    
    def __init__(self):
        '''
        Constructor
        '''
        self.events={}
        self.eventsByAcronym={}
  
    def add(self,event):
        self.events[event.event]=event
        
    def lookup(self,acronym):
        ''' lookup the given event '''
        result=None
        if acronym in self.events:
            result=self.events[acronym]
        elif acronym in self.eventsByAcronym:
            result=self.eventsByAcronym[acronym] 
        return result    
    
    def extractAcronyms(self):
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
    
    
    @staticmethod
    def isCached(mode='json'):
        if mode=='json':
            result=os.path.isfile(EventManager.getCacheFile()+".json")
        return result
        
    @staticmethod
    def getCacheFile():    
        path=os.path.dirname(__file__)
        cachedir=path+"/../cache/"
        return cachedir+"events"
    
    @staticmethod
    def fromStore(mode='json'):
        cacheFile=EventManager.getCacheFile()
        em=None
        if mode=="json":   
            em=JsonAbleMixin.readJson(cacheFile)
        return em
        
    def store(self,mode="json"):
        ''' store me '''
        cacheFile=EventManager.getCacheFile()
        if mode=="json":    
            self.writeJson(cacheFile)
    

class Event(object):
    '''
    an Event
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def fromAskResult(self,askRecord):
        ''' initialize me from the given ask result'''
        d=self.__dict__
        for key in ["event","series","acronym","title","city","homepage","country","start_date","end_date","creation_date","modification_date"]:
            if key in askRecord:
                d[key]=askRecord[key]
        ''' individual fixes '''
        if self.acronym is None:
            self.acronym=self.event
        if self.country is not None:
            if type(self.country) is list:
                print("warning country for %s is a list: %s" % (self.event,self.country))
            else:
                self.country=self.country.replace("Category:","")     
        self.url="https://www.openresearch.org/wiki/%s" % (self.event)       
    
    def asJson(self):
        ''' return me as a JSON record 
        https://stackoverflow.com/a/36142844/1497139 '''
        return json.dumps(self.__dict__,indent=4,sort_keys=True, default=str)
        
    
    def __str__(self):
        ''' create a string representation of this title '''
        text=self.homepage
        return text
