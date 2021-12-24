'''
Created on 2020-07-11

@author: wf
'''
import os
from ptp.titleparser import TitleParser
from corpus.event import Event,EventManager
class WikiData(object):
    '''
    WikiData proceedings titles event source
    '''
    defaultEndpoint="https://query.wikidata.org/sparql"


    def __init__(self, config=None):
        '''
        Constructor

        Args:
            config(StorageConfig): the storage configuration to use
        '''
        self.em=EventManager('wikidata',url='https://www.wikidata.org/wiki/Wikidata:Main_Page',title='Wikidata',config=config)
        self.debug=self.em.config.debug
        self.profile=self.em.config.profile
        path=os.path.dirname(__file__)
        self.sampledir=path+"/../sampledata/"
        self.sampleFilePath=self.sampledir+"proceedings-wikidata.txt"

    def cacheEvents(self,limit=1000000,batchSize=500):
        '''
        initialize me from my sample file

        Args:
            limit(int): the maximum number of events to cache
            batchSize(int): the batchSize to use
        '''
        tp=TitleParser.getDefault(self.em.name)
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
