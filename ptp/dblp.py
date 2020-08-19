'''
Created on 2020-07-17

@author: wf
'''
from ptp.event import EventManager, Event
import os
import json

class Dblp(object):
    '''
    https://dblp.org/ event managing
    see e.g. https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/25
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.em=EventManager('dblp',url='https://dblp.org/',title='dblp computer science bibliography')
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.jsonFilePath=self.jsondir+"dblp.json"
        
    def cacheEvents(self):
        ''' initialize me from my json file '''
        with open(self.jsonFilePath) as jsonFile:
            self.rawevents=json.load(jsonFile)
        if 'dblp' in self.rawevents:
            self.rawevents=self.rawevents['dblp']
        if 'proceedings' in self.rawevents:
            self.rawevents=self.rawevents['proceedings']
        for rawevent in self.rawevents:
            rawevent['eventId']=rawevent['@key']
            if 'year' in rawevent and 'booktitle' in rawevent:
                rawevent['acronym']="%s %s" % (rawevent['booktitle'],rawevent['year'])
            event=Event()
            event.fromDict(rawevent)
            event.source=self.em.name
            if 'url' in rawevent:
                event.url='https://dblp.org/%s' % rawevent['url']
            self.em.add(event)    
        self.em.store()        
                
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms()            
        