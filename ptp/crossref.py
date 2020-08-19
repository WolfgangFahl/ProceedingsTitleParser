'''
Created on 2020-07-05

@author: wf
'''
import habanero
from ptp.event import Event,EventManager
import json
import os
import re
import glob
import time
import datetime

class Crossref(object):
    '''
    Access to Crossref's search api see https://github.com/CrossRef/rest-api-doc
    '''

    def __init__(self, limit=1000000,batchSize=1000,debug=False,profile=False,mode='sparql',host=None,endpoint=None):
        '''
        Constructor
        '''
        self.profile=profile
        self.limit=limit
        self.batchSize=batchSize
        self.cr=habanero.Crossref()
        self.debug=debug
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.em=EventManager('crossref',url='https://www.crossref.org/',title='crossref.org',profile=profile,debug=debug,mode=mode)
        
    def cacheEvents(self):
        '''
        cache my json files to my eventmanager
        '''
        startTime=time.time()
        for jsonFilePath in self.jsonFiles():
            eventBatch=self.fromJsonFile(jsonFilePath)
            if self.debug:
                print("%4d: %s" % (len(eventBatch),jsonFilePath))
            for rawEvent in eventBatch:
                self.addEvent(rawEvent)
        if self.profile:
            print ("read %d events in %5.1f s" % (len(self.em.events),time.time()-startTime))
        self.em.store(self.limit,self.batchSize)
        
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()    
        
    def addEvent(self,rawEvent):
        '''
        add the given rawEvent e.g.
         {
        "event": {
          "name": "Adriatico Research Conference and Workshop",
          "location": "ICTP, Trieste, Italy"
        },
        "title": [
          "Towards the Theoretical Understanding of High Tc Superconductors"
        ],
        "DOI": "10.1142/0638"
      },

        '''
        event=Event()
        eventInfo=rawEvent['event']
        eventInfo['source']=self.em.name
        if 'title' in rawEvent: eventInfo['title']=rawEvent["title"][0]
        Event.fixEncodings(eventInfo,self.debug)
                            
        doi=rawEvent["DOI"]
        eventInfo['id']=doi
        if 'start' in eventInfo: self.getDateParts(eventInfo,'start')
        if 'end'   in eventInfo: self.getDateParts(eventInfo,'end')
        event.fromDict(eventInfo)
        self.em.add(event)
        
    
        
    def getDateParts(self,eventInfo,key):
        '''
        get a date from the json dict created by crossref e.g.
        "date-parts": [
              [
                1999,
                9,
                5
              ]
            ]

        '''
        if 'date-parts' in eventInfo[key]:
            dateparts=eventInfo[key]['date-parts']
            datetuple=tuple(dateparts[0])
            year=None
            month=None
            if len(datetuple)==3:
                year,month,day=datetuple
                dt = datetime.datetime(year=year,month=month,day=day)
                date=dt.date()
                eventInfo["%sDate" %(key)]=date
                eventInfo.pop(key)
            elif len(datetuple)==2:
                year,month=datetuple
            elif len(datetuple)==1:
                year=datetuple    
            else:
                if self.debug:
                    print("warning invalid date-tuple %s found" % (str(datetuple)))
            if year is not None: eventInfo["year"]=year
            if month is not None: eventInfo["month"]=month
                       
    
    def jsonFiles(self):  
        '''
        get the list of the json files that have my data
        '''
        jsonFiles=sorted(glob.glob(self.jsondir+"crossref-*.json"),key=lambda path:int(re.findall(r'\d+',path)[0]))
        return jsonFiles
    
    def fromJsonFile(self,jsonFilePath):
        '''
        get a single batch of events from the given jsonFilePath
        '''
        eventBatch=None
        with open(jsonFilePath) as jsonFile:
            response=json.load(jsonFile)  
            if 'status' in response:
                if response['status']=='ok':
                    eventBatch=response['message']['items']
        return eventBatch
    def doiMetaData(self,doi):
        ''' get the meta data for the given doi '''
        metadata=None
        response=self.cr.works([doi])
        if 'status' in response and 'message' in response and response['status']=='ok':
            metadata=response['message']
        return metadata