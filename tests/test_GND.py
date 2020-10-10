'''
Created on 2020-09-14

@author: wf
'''
import unittest
from ptp.gnd import GND
from lodstorage.sparql import SPARQL
from storage.query import Query
import getpass

class TestGND(unittest.TestCase):
    '''
    test GND data access
    '''


    def setUp(self):
        self.debug=True
        self.endpoint="http://jena.zeus.bitplan.com/gnd/"
        pass


    def tearDown(self):
        pass


    def testGND(self):
        '''
        test GND data access
        '''
        # get samples now has an Event_gnd.db download to prefill cache
        #if getpass.getuser()!="wf":
        #    return
        gnd=GND(endpoint=self.endpoint)
        gnd.initEventManager()
        cachedEvents=len(gnd.em.events)
        print("There are %d GND events available" % cachedEvents)
        # the GND subset of events with homepages has some 14281 events
        minTotal=14000
        self.assertTrue(cachedEvents>minTotal)
        debug=False
        invalid=0
        for i,event in enumerate(gnd.em.events.values()):
            dateRange=(gnd.getDateRange(event.date))
            if (len(dateRange)==0 and event.date is not None):
                invalid+=1
                if debug:
                    print("%5d: %s: %s %s" % (i,event.eventId,event.date,dateRange))
        if debug:
            print("%d GND dates are invalid " % invalid)
        self.assertTrue(invalid<minTotal/300)
        pass

    def testStats(self):
        if getpass.getuser()!="wf":
            return
        queries=[Query('entities and usage frequency', '''
# get histogramm data of entities by
# usage frequency
# WF 2020-06-27
PREFIX gnd: <https://d-nb.info/standards/elementset/gnd#>

SELECT ?c  (COUNT(?c) AS ?count)
WHERE {
  ?subject a  ?c
}
GROUP BY ?c
HAVING (?count >100)
ORDER BY DESC(?count)
        '''),Query('relevance of fields','''# get histogramm data of properties by
# usage frequency
# WF 2020-07-12
PREFIX gnd: <https://d-nb.info/standards/elementset/gnd#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX wdrs: <http://www.w3.org/2007/05/powder-s#>

SELECT ?property (COUNT(?property) AS ?propTotal)
WHERE { ?s ?property ?o . }
GROUP BY ?property
HAVING (?propTotal >1000)
ORDER BY DESC(?propTotal)''')
        ]
        sparql=SPARQL(self.endpoint)
        for query in queries:
            listOfDicts=sparql.queryAsListOfDicts(query.query)
            markup=query.asWikiMarkup(listOfDicts)
            markup=markup.replace("https://d-nb.info/standards/elementset/gnd","gnd")
            print ("=== %s ===" % query.name)
            print(markup)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
