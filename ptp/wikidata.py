'''
Created on 2020-07-11

@author: wf
'''
import os
import ptp.lookup
from ptp.event import EventManager, Event
class WikiData(object):
    '''
    WikiData proceedings titles event source
    '''

    def __init__(self, debug=False,profile=True):
        '''
        Constructor
        '''
        self.debug=debug
        self.profile=profile
        self.em=EventManager('wikidata',url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata')
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        self.sampleFilePath=self.sampledir+"proceedings-wikidata.txt"
        
    def cacheEvents(self,limit=1000000,batchSize=500):
        ''' initialize me from my sample file '''
        self.lookup=ptp.lookup.Lookup("wikidata",getAll=False)
        tp=self.lookup.tp
        tp.fromFile(self.sampleFilePath, "wikidata")
        tc,errs,result=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(result)))
        for title in result:
            if 'acronym' in title.metadata():
                if self.debug:
                    print(title.metadata())
            if 'eventId' in title.info:  
                event=Event()
                event.fromTitle(title,self.debug)
                event.eventId=event.eventId.replace("http://www.wikidata.org/entity/","")
                event.url="%s" % (title.info['eventId'])
                self.em.add(event)     
        self.em.store(limit=limit,batchSize=batchSize)
            
    def initEventManager(self):
        ''' init my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()
        