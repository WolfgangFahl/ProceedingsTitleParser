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

    def __init__(self,config=None):
        '''
        Constructor
        Args:
            config(StorageConfig): the storage configuration to use
        '''
        self.em=EventManager('dblp',url='https://dblp.org/',title='dblp computer science bibliography',config=config)
        self.debug=self.em.config.debug
        self.profile=self.em.config.profile
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.jsonFilePath=self.jsondir+"dblp.json"
        
    def cacheEvents(self,maxWarnings=10):
        ''' initialize me from my json file '''
        with open(self.jsonFilePath) as jsonFile:
            self.rawevents=json.load(jsonFile)
        if 'dblp' in self.rawevents:
            self.rawevents=self.rawevents['dblp']
        if 'proceedings' in self.rawevents:
            self.rawevents=self.rawevents['proceedings']
        warnings=0    
        for rawevent in self.rawevents:
            rawevent['eventId']=rawevent.pop('@key')
            if 'year' in rawevent and 'booktitle' in rawevent:
                rawevent['acronym']="%s %s" % (rawevent['booktitle'],rawevent['year'])
            if 'year' in rawevent:
                rawevent['year']=int(rawevent['year'])    
            if '@mdate' in rawevent:
                rawevent['mdate']=rawevent.pop('@mdate')
            else:
                rawevent['mdate']=None
            # publtype informal/withdrawn only used 2 x in over 40.0000 entries ...
            if not '@publtype' in rawevent:
            #    rawevent['publtype']=rawevent.pop('@publtype')    
            #else:
            #    rawevent['publtype']=None    
                event=Event()
                for checkKey in ['booktitle','ee','editor','isbn','lookupAcronym','note','publisher','series','title','volume','url']:
                    if not checkKey in rawevent:
                        rawevent[checkKey]=None
                    else:
                        value=rawevent[checkKey]
                        if type(value) is list:
                            value=value[0]
                            if warnings<maxWarnings:
                                print("warning %s has %d values" %(checkKey,len(value)))
                                warnings+=1
                            if checkKey=='editor':
                                if '@orcid' in value:
                                    rawevent['editorOrcid']=value['@orcid']
                            rawevent[checkKey]=value
                        if type(value) is dict:    
                #  'ee': {'@type': 'oa', '#text': 'http://ceur-ws.org/Vol-1974'} 
                # 'title': {'sup': 'th', '#text': 'Usability ...           
                            value=value['#text']   
                            rawevent[checkKey]=value 
                self.em.setNone(rawevent, ['editorOrcid'])            
                event.fromDict(rawevent)
                event.source=self.em.name
                # make sure the values are set and there are not multiple ones
                # if the value is a dict extract the #text attribute        
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
        
