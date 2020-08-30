'''
Created on 2020-07-04

@author: wf
'''
import csv
import io
import json
import re
import os
import time

from storage.entity import EntityManager
from storage.config import StoreMode
import pyparsing as pp

class EventManager(EntityManager):
    ''' handle a catalog of events '''
    debug=False
    
    def __init__(self,name,url=None,title=None,config=None):
        '''
        Constructor
        
        Args:
            name(string): the name of this event manager e.g. "confref"
            url(string): the url of the event source  e.g. "http://portal.confref.org/"
            title(string): title of the event source e.g. "confref.org"
        '''
        super().__init__(name,entityName="Event",entityPluralName="Events",config=config)
        self.url=url
        self.title=title
        self.events={}
        self.eventsByAcronym={}
        self.eventsByCheckedAcronym={}
        self.config.tableName="Event_%s" % self.name
  
    def add(self,event):
        ''' add the given event '''
        self.events[event.eventId]=event
        if hasattr(event,"lookupAcronym"):
            self.eventsByAcronym[event.lookupAcronym]=event
        
    def lookup(self,acronym):
        ''' lookup the given event '''
        foundEvents=[]
        if acronym in self.events:
            foundEvent=self.events[acronym]
            foundEvent.lookedUpIn="events"
            foundEvents=[foundEvent]
        elif acronym in self.eventsByCheckedAcronym:
            foundEvents=self.eventsByCheckedAcronym[acronym]
            for foundEvent in foundEvents:
                foundEvent.lookedUpIn="checked acronyms" 
        elif acronym in self.eventsByAcronym:
            foundEvent=self.eventsByAcronym[acronym]    
            foundEvent.lookedUpIn="acronyms" 
            foundEvents=[foundEvent]
        return foundEvents
    
    def extractCheckedAcronyms(self):
        ''' extract checked acronyms '''
        self.showProgress("extracting acronyms for %s" % (self.name))
        self.eventsByCheckedAcronym={}
        grammar= pp.Regex(r'^(([1-9][0-9]?)th\s)?(?P<acronym>[A-Z/_-]{2,11})[ -]*(19|20)[0-9][0-9]$')
        for event in self.events.values():
            if hasattr(event, 'acronym') and event.acronym is not None:
                try:
                    val=grammar.parseString(event.acronym).asDict()
                    if "acronym" in val:
                        acronym=val['acronym']
                        if acronym in self.eventsByCheckedAcronym:
                            self.eventsByCheckedAcronym[acronym].append(event)
                        else:
                            self.eventsByCheckedAcronym[acronym]=[event]    
                except pp.ParseException as pe:
                    if EventManager.debug:
                        print(event.acronym)
                        print(pe)
                    pass
        self.showProgress ("found %d checked acronyms for %s of %d events with acronyms" % (len(self.eventsByCheckedAcronym),self.name,len(self.eventsByAcronym)))          
    
    def removeCacheFile(self):
        '''  remove my cache file '''
        if self.mode=='json':
            cacheFile=self.getCacheFile()
            if os.path.isfile(cacheFile):
                os.remove(cacheFile)
        elif self.mode=='dgraph':
            # https://discuss.dgraph.io/t/running-upsert-in-python/9364
            """mutation='''
            upsert {  
  query {
    # get the uids of all Event nodes
     events as var (func: has(<dgraph.type>)) @filter(eq(<dgraph.type>, "Country")) {
        uid
    }
  }
  mutation {
    delete {
      uid(events) * * .
    }
  }
}'''        
            self.dgraph.query(mutation)"""
    
    def fromEventList(self,eventList):
        ''' 
        restore my events form the given ListOfDicts
        Args:
           eventList(list): the list of event Records/Dicts
        '''
        for eventRecord in eventList:
            event=Event()
            event.fromDict(eventRecord)
            self.add(event)
    
    def fromStore(self,cacheFile=None):
        '''
        restore me from the store
        Args:
            cacheFile(String): the cacheFile to use if None use the preconfigured Cachefile
        '''
        startTime=time.time()
        listOfDicts=super().fromStore(cacheFile)
        if self.config.mode is StoreMode.JSON:
            em=listOfDicts
            if em is not None:
                if em.events is not None:
                    self.events=em.events    
                    self.showProgress("read %d %s from %s in %5.1f s" % (len(em.events),self.entityPluralName,self.name,time.time()-startTime))     
 
                if em.eventsByAcronym:
                    self.eventsByAcronym=em.eventsByAcronym  
        else:
            self.fromEventList(listOfDicts)
       
    def getListOfDicts(self):
        '''
        get the list of Dicts for me
        '''
        eventList=[]
        for event in self.events.values():
            d=event.__dict__
            eventList.append(d)
        return eventList
                    
    def store(self,cacheFile=None,batchSize=2000,limit=None):
        '''
        store my events
        
        Args:
            cacheFile(string): the cacheFile to use 
        '''
        super().store(self.getListOfDicts(),cacheFile=cacheFile,batchSize=batchSize,limit=limit)  
  
    @staticmethod
    def asWikiSon(eventDicts):  
        wikison=""
        for eventDict in eventDicts:
            wikison+=EventManager.eventDictToWikiSon(eventDict)
        return wikison
    
    @staticmethod
    def asCsv(eventDicts):
        ''' convert the given event dicts to CSV 
        see https://stackoverflow.com/a/9157370/1497139'''  
        output=io.StringIO()
        fieldNameSet=set()
        for eventDict in eventDicts:
            for key in eventDict.keys():
                fieldNameSet.add(key)
        writer=csv.DictWriter(output,fieldnames=list(fieldNameSet),quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for eventDict in eventDicts:
            writer.writerow(eventDict)
        return output.getvalue()
    
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
        self.acronym=None
        self.city=None
        self.country=None
        
    def hasUrl(self):
        result=False
        if (hasattr(self,'homepage') and self.homepage is not None):
            result=True
        else:
            result=hasattr(self,'url')
        return result  
    
    def getUrl(self):
        if hasattr(self,'url'): 
            return self.url
        else:
            return self.homepage
        
    def fromAskResult(self,askRecord):
        ''' initialize me from the given ask result'''
        d=self.__dict__
        for key in ["event","series","acronym","title","city","homepage","country","start_date","end_date","creation_date","modification_date"]:
            if key in askRecord:
                d[key]=askRecord[key]
        ''' individual fixes '''
        if self.series is not None:
            if type(self.series) is list:
                print("warning series for %s is a list: %s - using only 1st entry" % (self.event,self.series))
                self.series=self.series[0]
        if self.country is not None:
            if type(self.country) is list:
                print("warning country for %s is a list: %s" % (self.event,self.country))
            else:
                self.country=self.country.replace("Category:","")   
        self.eventId=self.event          
        self.url="https://www.openresearch.org/wiki/%s" % (self.event) 
        self.getLookupAcronym()
            
    def fromTitle(self,title,debug=False):
        ''' fill my data from the given Title '''
        md=title.metadata()
        Event.fixEncodings(md,debug)  
        # fix event field
        if 'event' in md:
            md['eventType']=md['event']
        self.fromDict(md)
        self.getLookupAcronym()
            
    def fromDict(self,srcDict):
        ''' fill my data from the given source Dict'''
        d=self.__dict__
        for key in srcDict:
            targetKey=key
            if key=="id":
                targetKey='eventId'
            value=srcDict[key]
            d[targetKey]=value        
        self.getLookupAcronym()         
    
    def getLookupAcronym(self):
        ''' get the lookup acronym of this event e.g. add year information '''
        if hasattr(self,'acronym') and self.acronym is not None:
            self.lookupAcronym=self.acronym
        else:
            if hasattr(self,'event'):
                self.lookupAcronym=self.event
        if hasattr(self,'lookupAcronym'):
            if self.lookupAcronym is not None:
                try:
                    if hasattr(self, 'year') and self.year is not None and not re.search(r'[0-9]{4}',self.lookupAcronym):
                        self.lookupAcronym="%s %s" % (self.lookupAcronym,str(self.year))
                except TypeError as te:
                    print ('Warning getLookupAcronym faile for year: %s and lookupAcronym %s' % (self.year,self.lookupAcronym)) 
        
    @staticmethod    
    def fixEncodings(eventInfo,debug=False):    
        for keyValue in eventInfo.items():
            key,value=keyValue
            oldvalue=value
            if isinstance(value,str):
                # work around Umlaut encodings like "M\\"unster"
                # and \S encoded as \\S
                found=False
                for umlautTuple in [('\\"a',"ä"),('\\"o',"ö"),('\\"u',"ü"),('\\',' ')]:
                    uc,u=umlautTuple
                    if uc in value:
                        value=value.replace(uc,u)
                        found=True
                if found:
                    if debug:
                        print("Warning: fixing '%s' to '%s'" % (oldvalue,value))
                    eventInfo[key]=value       
    
    def asJson(self):
        ''' return me as a JSON record 
        https://stackoverflow.com/a/36142844/1497139 '''
        return json.dumps(self.__dict__,indent=4,sort_keys=True, default=str)
    
    def __str__(self):
        ''' create a string representation of this title '''
        text="%s (%s)" % (self.homepage,self.foundBy)
        return text
