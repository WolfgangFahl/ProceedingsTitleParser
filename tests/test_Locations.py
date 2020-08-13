'''
Created on 2020-08-11

@author: wf
'''
import unittest
import time
from storage.dgraph import Dgraph
from ptp.location import CountryManager, CityManager
from ptp.listintersect import ListOfDict
import datetime
from collections import Counter

class TestLocations(unittest.TestCase):
    '''
    check countries, provinces/states and cities
    '''


    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass
    
    def testCities(self):
        '''
        test consolidating cities from different sources
        '''
        cim=CityManager()
        startTime=time.time()
        cim.fromLutangar()
        self.assertEqual(128769,(len(cim.cityList)))
        print ("reading %d cities from github took %5.1f secs" % (len(cim.cityList),time.time()-startTime))
        startTime=time.time()
        orCities=cim.fromOpenResearch(showProgress=True)
        cityCounter=Counter(orCities)
        uniqueCities=list(cityCounter.most_common())
        print ("reading %d cities from %d events from openresearch took %5.1f secs" % (len(uniqueCities),len(orCities),time.time()-startTime))
        print (cityCounter.most_common(100))
        orCityList=[]
        for cityName,count in uniqueCities:
            orCityList.append({'name': cityName, 'count': count})
        startTime=time.time()
        validCities=ListOfDict().intersect(cim.cityList, orCityList, 'name')
        print ("validating %d cities from openresearch took %5.1f secs" % (len(validCities),time.time()-startTime))
     

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