'''
Created on 2020-07-04

@author: wf
'''
import csv
import io
import json
import re
import os
from storage.yamlablemixin import YamlAbleMixin
from storage.jsonablemixin import JsonAbleMixin
from storage.dgraph import Dgraph
from storage.sparql import SPARQL
import pyparsing as pp
import time

class EventManager(YamlAbleMixin, JsonAbleMixin):
    ''' handle a catalog of events '''
    debug=False
    
    def __init__(self,name,url=None,title=None,debug=False,mode='json',withShowProgress=True,host='localhost', endpoint=None, profile=False):
        '''
        Constructor
        '''
        self.name=name
        self.mode=mode
        self.url=url
        self.title=title
        self.events={}
        self.eventsByAcronym={}
        self.eventsByCheckedAcronym={}
        self.withShowProgress=True
        self.debug=debug
        self.profile=profile
        self.showProgress ("Creating Eventmanager(%s) for %s" % (self.mode,self.name))
        if self.mode=='dgraph':
            self.dgraph=Dgraph(debug=self.debug,host=host,profile=self.profile)
        if self.mode=='sparql':
            if endpoint is None:
                raise Exception("no endpoint set for mode sparql")    
            self.endpoint=endpoint    
        
    def showProgress(self,msg):
        ''' display a progress message '''
        if self.withShowProgress:
            print (msg,flush=True)    
  
    def add(self,event):
        ''' add the given event '''
        self.events[event.event]=event
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
        self.showProgress ("found %d checked acronyms of %d events with acronyms" % (len(self.eventsByCheckedAcronym),len(self.eventsByAcronym)))          
    
    def isCached(self):
        ''' check whether there is a file containing cached 
        data for me '''
        result=os.path.isfile(self.getCacheFile())
        return result
    
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
                    
        
    def getCacheFile(self):
        ''' get the path to the file for my cached data '''    
        path=os.path.dirname(__file__)
        cachedir=path+"/../cache"
        cachepath="%s/%s-%s.%s" % (cachedir,self.name,"events",self.mode)
        return cachepath
    
    def fromStore(self):
        '''
        restore me from the store
        '''
        cacheFile=self.getCacheFile()
        self.showProgress("reading events from cache %s" % (cacheFile))
        em=None
        if self.mode=="json":   
            em=JsonAbleMixin.readJson(cacheFile)
        elif self.mode=="sparql":
            eventQuery="""
            PREFIX cr: <http://cr.bitplan.com/>
SELECT ?eventId ?acronym ?name ?year ?country ?city ?startDate ?endDate ?url ?source WHERE { 
   ?event cr:Event_eventId ?eventId.
   ?event cr:Event_acronym ?acronym.
   ?event cr:Event_name ?name.
   ?event cr:Event_year ?year.  
   ?event cr:Event_country ?country.
   ?event cr:Event_city ?city.
   ?event cr:Event_startDate ?startDate.
   ?event cr:Event_endDate ?endDate.
   ?event cr:Event_url ?url.
   ?event cr:Event_source ?source.
}
"""    
        else:
            raise Exception("unsupported store mode %s",self.mode)
        if em is not None:
            if em.events is not None:
                self.events=em.events     
            if em.eventsByAcronym:
                self.eventsByAcronym=em.eventsByAcronym    
        self.showProgress("found %d events" % (len(self.events)))        
    
    def getListOfDicts(self):
        eventList=[]
        for event in self.events.values():
            d=event.__dict__
            eventList.append(d)
        return eventList
                    
    def store(self,limit=10000000,batchSize=250):
        ''' store me '''
        if self.mode=="json":    
            cacheFile=self.getCacheFile()
            self.showProgress ("storing %d events to cache %s" % (len(self.events),cacheFile))
            self.writeJson(cacheFile)
        elif self.mode=="dgraph":
            eventList=self.getListOfDicts()
            startTime=time.time()
            self.showProgress ("storing %d events to %s" % (len(self.events),self.mode))    
            self.dgraph.addData(eventList,limit=limit,batchSize=batchSize)
            self.showProgress ("store done after %5.1f secs" % (time.time()-startTime))
        elif self.mode=="sparql":
            eventList=self.getListOfDicts()
            sparql=SPARQL(self.endpoint,debug=self.debug,profile=self.profile)
            startTime=time.time()
            self.showProgress ("storing %d events to %s" % (len(self.events),self.mode))    
            entityType="cr:Event"
            prefixes="PREFIX cr: <http://cr.bitplan.com/>"
            primaryKey="identifier"
            sparql.insertListOfDicts(eventList, entityType, primaryKey, prefixes,limit=limit,batchSize=batchSize)
            self.showProgress ("store done after %5.1f secs" % (time.time()-startTime))
        else:
            raise Exception("unsupported store mode %s" % self.mode)    
  
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
        if self.country is not None:
            if type(self.country) is list:
                print("warning country for %s is a list: %s" % (self.event,self.country))
            else:
                self.country=self.country.replace("Category:","")     
        self.url="https://www.openresearch.org/wiki/%s" % (self.event) 
        self.getLookupAcronym()
            
    def fromTitle(self,title):
        ''' fill my data from the given Title '''
        md=title.metadata()
        # fix event field
        if 'event' in md:
            md['eventType']=md['event']
        self.fromDict(md)
        self.getLookupAcronym()
            
    def fromDict(self,srcDict):
        ''' fill my data from the given source Dict'''
        if 'acronym' in srcDict:
            srcDict['event']=srcDict['acronym']
        d=self.__dict__
        for key in srcDict:
            targetKey=key
            if key=="id":
                targetKey='identifier'
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
            if hasattr(self, 'year') and not re.search(r'[0-9]{4}',self.lookupAcronym):
                self.lookupAcronym="%s %s" % (self.lookupAcronym,str(self.year))
            pass       
    
    def asJson(self):
        ''' return me as a JSON record 
        https://stackoverflow.com/a/36142844/1497139 '''
        return json.dumps(self.__dict__,indent=4,sort_keys=True, default=str)
    
    def __str__(self):
        ''' create a string representation of this title '''
        text="%s (%s)" % (self.homepage,self.foundBy)
        return text
