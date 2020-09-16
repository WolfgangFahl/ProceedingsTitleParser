'''
Created on 2020-09-15

@author: wf
'''
from ptp.event import Event,EventManager
from storage.sparql import SPARQL
import time

class GND(object):
    '''
    manages event data from Gemeinsame Normdatei
    https://d-nb.info/standards/elementset/gnd
    '''

    def __init__(self,config=None,endpoint=None):
        '''
        Constructor
        '''
        self.em=EventManager('gnd',url='https://d-nb.info/standards/elementset/gnd',title='GND',config=config)
        self.endpoint=endpoint
        
    def cacheEvents(self):
        '''
        cache my events
        '''
        self.fromRDF(self.endpoint)
        pass
    
    def fromRDF(self,endpoint):
        '''
        retrieve my event list from the given SPARQL endpoint
        '''
        # get SPARQL access to GND data
        print ("Retrieving %s events from SPARQL endpoint %s\n  ... this might take a few minutes ..." % (self.em.title,endpoint))
        starttime=time.time()
        gndEp=SPARQL(endpoint)
        queryString="""# get events with most often used columns from GND
# plus acronym, topic, homepage (seldom but useful)
# WF 2020-07-12
PREFIX gndi:  <https://d-nb.info/gnd>
PREFIX gnd:  <https://d-nb.info/standards/elementset/gnd#>
PREFIX gndo: <https://d-nb.info/standards/vocab/gnd/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX wdrs: <http://www.w3.org/2007/05/powder-s#>

SELECT  ?event ?eventId ?acronym  ?variant ?title ?date ?areaCode ?place ?topic ?homepage 
WHERE {
  ?event a gnd:ConferenceOrEvent.
  ?event gnd:gndIdentifier ?eventId.
  OPTIONAL { ?event gnd:abbreviatedNameForTheConferenceOrEvent ?acronym. }
  OPTIONAL { ?event gnd:variantNameForTheConferenceOrEvent ?variant.}
  OPTIONAL { ?event gnd:preferredNameForTheConferenceOrEvent ?title.}
  OPTIONAL { ?event gnd:dateOfConferenceOrEvent ?date. }
  OPTIONAL { ?event gnd:geographicAreaCode ?areaCode. }
  OPTIONAL { ?event gnd:placeOfConferenceOrEvent ?place. }
  OPTIONAL { ?event gnd:topic ?topic. }
  { ?event gnd:homepage ?homepage. }
}
#LIMIT 10000"""    
        results=gndEp.query(queryString)
        eventList=gndEp.asListOfDicts(results)
        print ("retrieved %d events in %6.1f s" % (len(eventList),time.time()-starttime))
        for rawevent in eventList:
            rawevent['url']=rawevent.pop('event')
            fields=['eventId','variant','name','areaCode','url','source','date','place','acronym','lookupAcronym','topic','homepage']
            self.em.setNone(rawevent,fields)
            event=Event()
            event.fromDict(rawevent)
            event.source=self.em.name
            self.em.add(event)    
        self.em.store(sampleRecordCount=10000)   
        
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        #self.em.extractCheckedAcronyms()    
