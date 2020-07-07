'''
Created on 2020-07-06

@author: wf
'''
import os
from ptp.lookup import Lookup
from ptp.event import EventManager

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
        
    def cacheEvents(self):
        ''' test caching the events of CEUR-WS derived from the sample proceeding titles'''
        self.lookup=Lookup("CEUR-WS")
        tp=self.lookup.tp
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tc,errs,result=tp.parseAll()
        if self.debug:
            print(tc)
            print("%d errs %d titles" % (len(errs),len(result)))
        self.em=EventManager("ceur-ws")
        for title in result:
            if 'acronym' in title.metadata():
                if self.debug:
                    print(title.metadata())
                    
                    
        