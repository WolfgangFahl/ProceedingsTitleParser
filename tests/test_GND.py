'''
Created on 2020-09-14

@author: wf
'''
import unittest
from storage.sparql import SPARQL
from lodstorage.sql import SQLDB
from storage.entity import EntityManager
import getpass
import os

class TestGND(unittest.TestCase):
    '''
    test GND data access
    '''


    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testGND(self):
        '''
        test GND data access
        '''
        if getpass.getuser()!="wf":
            return
        em=EntityManager("Event_GND","Event","Events")
        em.config.tableName="Event_GND"
        dbFile=em.getCacheFile(em.config)
        if os.path.isfile(dbFile):
            print("%s already exists" %dbFile,flush=True)
        else:
            print("creating %s via SPARQL query" % dbFile,flush=True)
       
            endpoint="http://jena.zeus.bitplan.com/gnd/"
            # get SPARQL access to GND data
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

SELECT  ?event ?eventId ?acronym  ?variant ?name ?date ?areaCode ?place ?topic ?homepage 
WHERE {
  ?event gnd:gndIdentifier ?eventId.
  OPTIONAL { ?event gnd:abbreviatedNameForTheConferenceOrEvent ?acronym. }
  OPTIONAL { ?event gnd:variantNameForTheConferenceOrEvent ?variant.}
  OPTIONAL { ?event gnd:preferredNameForTheConferenceOrEvent ?name.}
  OPTIONAL { ?event gnd:dateOfConferenceOrEvent ?date. }
  OPTIONAL { ?event gnd:geographicAreaCode ?areaCode. }
  OPTIONAL { ?event gnd:placeOfConferenceOrEvent ?place. }
  OPTIONAL { ?event gnd:topic ?topic. }
  OPTIONAL { ?event gnd:homepage ?homepage. }
}
#LIMIT 10000"""
            results=gndEp.query(queryString)
            eventList=gndEp.asListOfDicts(results)
            sqlDB=SQLDB(dbname=dbFile,debug=self.debug,errorDebug=True)
            entityName="Event_GND"
            primaryKey=None # not unique: "eventId"
            executeMany=False
            entityInfo=sqlDB.createTable(eventList[:10],entityName,primaryKey)
            print("found %d GND events" % (len(eventList)))
            em.setNone4List(eventList, ['acronym','variant','name','date','areaCode','place','topic','homepage'])
            sqlDB.store(eventList, entityInfo, executeMany=executeMany)
        #em.store(eventList,sampleRecordCount=1000)  
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()