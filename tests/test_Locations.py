'''
Created on 2020-08-11

@author: wf
'''
import unittest
import time
from storage.dgraph import Dgraph
from storage.sparql import SPARQL
from ptp.location import CountryManager, CityManager
from ptp.listintersect import ListOfDict
import datetime
from collections import Counter
import getpass
from tests.test_Jena import TestJena

class TestLocations(unittest.TestCase):
    '''
    check countries, provinces/states and cities
    '''
    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass
    
    def testCityStorage(self):
        '''
        try storing city data in cache
        '''
        cim=CityManager(name="github")
        cim.fromLutangar()
        cim.store(cim.cityList)
        
    
    def testCities(self):
        '''
        test consolidating cities from different sources
        '''
        cim=CityManager('lutangarVersusOpenResearch')
        startTime=time.time()
        cim.fromLutangar()
        self.assertEqual(128769,(len(cim.cityList)))
        print ("reading %d cities from github took %5.1f secs" % (len(cim.cityList),time.time()-startTime))
        startTime=time.time()
        orCities=cim.fromOpenResearch(showProgress=True)
        cityCounter=Counter(orCities)
        uniqueCities=list(cityCounter.most_common())
        print ("reading %d cities from %d events from openresearch took %5.1f secs" % (len(uniqueCities),len(orCities),time.time()-startTime))
        print (cityCounter.most_common(1000))
        orCityList=[]
        for cityName,count in uniqueCities:
            orCityList.append({'name': cityName, 'count': count})
        startTime=time.time()
        validCities=ListOfDict().intersect(cim.cityList, orCityList, 'name')
        print ("validating %d cities from openresearch took %5.1f secs" % (len(validCities),time.time()-startTime))
     
    def getDBPedia(self,mode='query',debug=False):
        endpoint="http://dbpedia.org/sparql"
        dbpedia=SPARQL(endpoint,mode=mode,debug=debug)
        return dbpedia
        
    def testDBPediaCities(self):
        '''
        https://github.com/LITMUS-Benchmark-Suite/dbpedia-graph-convertor/blob/master/get_data.py
        '''
        dbpedia=self.getDBPedia()
        limit=100
        # Query to get the population of cities
        citiesWithPopulationQuery = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            SELECT DISTINCT ?dbCity ?country ?name ?website ?population
            WHERE {
                ?dbCity a dbo:City .
                ?dbCity dbp:name ?name .
                ?dbCity dbo:country ?country .
                OPTIONAL { ?dbCity dbo:populationTotal ?population . }
                OPTIONAL { ?dbCity dbp:website ?website . }
            }
            LIMIT %d
            """ % limit
        cityList=dbpedia.queryAsListOfDicts(citiesWithPopulationQuery)
        cim=CityManager("dbpedia")      
        cim.setNone4List(cityList, ["population","website"])
        cim.store(cityList)
  
    def testDBPediaCountries(self):
        '''
        http://dbpedia.org/ontology/Country
        '''
        dbpedia=self.getDBPedia()
        countriesQuery="""
        # https://opendata.stackexchange.com/a/7660/18245 - dbp:iso3166code not set ...
        PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?country_name ?population ?isocode
WHERE {
  ?country_name a dbo:Country .
  ?country_name dbp:iso3166code ?isocode. 
  OPTIONAL { ?country_name dbo:populationTotal ?population . }
}
        """
        countriesResult=dbpedia.query(countriesQuery)
        print(countriesResult)
        print(len(countriesResult))
        
        
    def testWikiDataCountries(self):
        '''
        check local wikidata
        '''
        # check we have local wikidata copy:
        if getpass.getuser()=="wf":
            # use 2018 wikidata copy
            #endpoint="http://blazegraph.bitplan.com/sparql"
            # use 2020 wikidata copy
            endpoint="http://jena.bitplan.com/wikidata"
            cm=CountryManager()
            cm.fromWikiData(endpoint)      
            self.assertTrue(len(cm.countryList)>=195) 
            sparql=TestJena.getJena(debug=self.debug)
            errors=cm.storeToRDF(sparql)  
            self.assertFalse(sparql.printErrors(errors))
            doimport=True
            if doimport:
                cm2=CountryManager()
                cm2.fromRDF(sparql)
            self.assertEqual(cm.countryList,cm2.countryList)

    def testCountries(self):
        '''
        test consolidating countries from different sources
        '''
        cm=CountryManager()
        cm.fromErdem()
        cm.fromConfRef()
        dgraph=Dgraph(debug=self.debug)
        # drop all data and schemas
        dgraph.drop_all()
        # create schema for countries
        dgraph.addSchema(cm.schema)
        startTime=time.time()
        dgraph.addData(obj=cm.countryList)    
        elapsed=time.time() - startTime
        print("adding %d countries took %5.1f s" % (len(cm.countryList),elapsed)) 
        queryResult=dgraph.query(cm.graphQuery)
        self.assertTrue('countries' in queryResult)
        countries=queryResult['countries']
        self.assertEqual(len(countries),len(cm.countryList))
        validCountries=ListOfDict.intersect(countries, cm.confRefCountries, 'name')
        print("found %d valid countries " % (len(validCountries)))    
        self.assertEquals(138,len(validCountries))
        dgraph.close()
        pass
    
    def testIntersection(self):
        '''
        test creating the intersection of a list of dictionaries
        '''
        list1 = [{'count': 351, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
         {'count': 332, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
         {'count': 336, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
         {'count': 359, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
         {'count': 309, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'}]

        list2 = [{'count': 359, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
             {'count': 351, 'evt_datetime': datetime.datetime(2015, 10, 23, 8, 45), 'att_value': 'red'},
             {'count': 381, 'evt_datetime': datetime.datetime(2015, 10, 22, 8, 45), 'att_value': 'red'}]
        
        listi=ListOfDict.intersect(list1, list2,'count')
        print(listi)
        self.assertEquals(2,len(listi))
        listi=ListOfDict.intersect(list1, list2)
        print(listi)
        self.assertEquals(2,len(listi))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()