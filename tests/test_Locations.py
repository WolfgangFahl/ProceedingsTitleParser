'''
Created on 2020-08-11

@author: wf
'''
import unittest
import time
from dg.dgraph import Dgraph
from ptp.location import CountryManager
from ptp.listintersect import ListOfDict
import datetime

class TestLocations(unittest.TestCase):
    '''
    check countries, provinces/states and cities
    '''


    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


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