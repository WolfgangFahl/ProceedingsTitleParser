'''
Created on 2020-07-11

@author: wf
'''
from ptp.event import EventManager, Event
import os
import json

class ConfRef(object):
    '''
    classdocs
    '''

    def __init__(self,debug=False,mode='json',host='localhost',endpoint=None,profile=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.em=EventManager('confref',url='http://portal.confref.org/',title='confref.org',profile=profile,debug=debug,mode=mode,host=host,endpoint=endpoint)
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.jsonFilePath=self.jsondir+"confref-conferences.json"
        
    def cacheEvents(self,limit=1000000,batchSize=1000):
        ''' initialize me from my json file '''
        with open(self.jsonFilePath) as jsonFile:
            self.rawevents=json.load(jsonFile)
        for rawevent in self.rawevents:
            rawevent['eventId']=rawevent['id']
            event=Event()
            event.fromDict(rawevent)
            event.event=rawevent['id']
            event.source=self.em.name
            event.url='http://portal.confref.org/list/%s' % rawevent['id']
            self.em.add(event)    
        self.em.store(limit=limit,batchSize=batchSize)        
                
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()            
        
        