'''
Created on 2020-08-11

@author: wf
'''
import unittest
import time
from dg.dgraph import Dgraph
from ptp.location import CountryManager

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
     
        
        dgraph.close()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()