'''
Created on 2020-07-06

@author: wf
'''
import os
import ptp.lookup
from ptp.event import EventManager, Event

class CEURWS(object):
    '''
    http://ceur-ws.org/ event managing
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        self.em=EventManager("ceur-ws")
        
    def cacheEvents(self):
        ''' test caching the events of CEUR-WS derived from the sample proceeding titles'''
        self.lookup=ptp.lookup.Lookup("CEUR-WS",getAll=False)
        tp=self.lookup.tp
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tc,errs,result=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(result)))
        for title in result:
            if 'acronym' in title.metadata():
                if self.debug:
                    print(title.metadata())
                if 'id' in title.info:    
                    event=Event()
                    event.fromTitle(title)
                    event.url="http://ceur-ws.org/%s" % (title.info['id'])
                    self.em.add(event)     
        self.em.store()
            
    def initEventManager(self):
        ''' init my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractAcronyms()
        