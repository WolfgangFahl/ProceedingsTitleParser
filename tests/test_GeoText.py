'''
Created on 2020-09-08

@author: wf
'''
import unittest
from ptp.lookup import Lookup
from geotext import GeoText

import geograpy

class TestGeoText(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testGeoText(self):
        '''
        test the GeoText library
        '''
        
        sqlQuery="""select count(*) as count,
locality from event_wikicfp
where locality is not null
group by locality
order by 1 desc
LIMIT 100
"""
        lookup=Lookup()
        sqlDB=lookup.getSQLDB()
        if sqlDB is not None:
            listOfDicts=sqlDB.query(sqlQuery)
            for record in listOfDicts:
                locality=record['locality']
                print(locality)
                geo=GeoText(locality)
                print(" %s" % geo.countries)
                print(" %s" % geo.cities)
                gp=geograpy.get_place_context(text=locality)
                print(" %s" % gp.countries)
                print(" %s" % gp.regions)
                print(" %s" % gp.cities)
                
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()