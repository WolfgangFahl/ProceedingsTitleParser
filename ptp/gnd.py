'''
Created on 2020-09-15

@author: wf
'''
from ptp.event import Event,EventManager
from lodstorage.sparql import SPARQL
import re
import time
import datetime

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
    
    @staticmethod
    def strToDate(dateStr):
        result=datetime.datetime.strptime(
                        dateStr, "%d.%m.%Y").date()
        return result
                        
    @staticmethod
    def getDateRange(date):
        '''
        given a GND date string create a date range
        
        Args:
            date(str): the date string to analyze
            
        Returns:
            dict: containing year, startDate, endDate
        examples:
        2018-2019
        08.01.2019-11.01.2019
        2019
        '''
        result={}
        if date is not None:
            yearPattern="[12][0-9]{3}"
            datePattern="[0-9]{2}[.][0-9]{2}[.]"+yearPattern
            yearOnly=re.search(r"^("+yearPattern+")[-]?("+yearPattern+")?$",date)
            if yearOnly: 
                result['year']=int(yearOnly.group(1))
            else:                
                fromOnly=re.search(r"^("+datePattern+")[-]?$",date) 
                if fromOnly:   
                    result['startDate']=GND.strToDate(fromOnly.group(1))
                else:
                    fromTo=re.search(r"^("+datePattern+")[-]("+datePattern+")$",date)
                    if fromTo:
                        result['startDate']=GND.strToDate(fromTo.group(1))
                        result['endDate']=GND.strToDate(fromTo.group(2))
        if 'startDate' in result:
                result['year']=result['startDate'].year
        return result
    
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
            fields=['eventId','variant','name','areaCode','url','source','date','startDate','endDate','year','place','acronym','lookupAcronym','topic','homepage']
            self.em.setNone(rawevent,fields)
            dateStr=rawevent['date']
            for key,value in GND.getDateRange(dateStr).items():
                rawevent[key]=value
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
