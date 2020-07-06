'''
Created on 2020-07-06

@author: wf
'''
import os
from ptp.lookup import Lookup

class CEURWS(object):
    '''
    http://ceur-ws.org/ event managing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        
    def cacheEvents(self):
        ''' test caching the events of CEUR-WS derived from the sample proceeding titles'''
        lookup=Lookup("CEUR-WS")
        tp=lookup.tp
        samplefile=self.sampledir+"proceedings-ceur-ws.txt"
        tp.fromFile(samplefile, "CEUR-WS")
        tp.parseAll()
        