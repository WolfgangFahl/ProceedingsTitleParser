'''
Created on 2020-09-08

@author: wf
'''
import unittest
from ptp.lookup import Lookup
from lodstorage.sql import SQLDB
from geotext import GeoText

import geograpy
import os

class TestGeoText(unittest.TestCase):
    '''
    test the geo text  and similar libraries
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def checkExamples(self,examples,countries):
        '''
        
        check that the given example give results in the given countries
        Args:
            examples(list): a list of example location strings
            countries(list): a list of expected country iso codes
        '''
        for index,example in enumerate(examples):
            city=geograpy.locateCity(example,debug=False)
            if self.debug:
                print("%3d: %22s->%s" % (index,example,city))
            self.assertEqual(countries[index],city.country.iso) 

    def testGeoGrapyExamples(self):
        examples=['San Francisco, USA','Auckland, New Zealand']
        countries=['US','NZ']
        self.checkExamples(examples, countries)

    def testGeoTextAndGrapy(self):
        '''
        test the GeoText and geograpy3 library
        '''
        debug=True
        limit=100
        sqlQuery="""select count(*) as count,
locality from Event_wikicfp
where locality is not null
group by locality
order by 1 desc
LIMIT %d
""" % limit
        dbFile=Lookup.getDBFile()
        if os.path.isfile(dbFile):
            sqlDB=SQLDB(dbFile)
        else:
            lookup=Lookup.ensureAllIsAvailable("testGeoText")
            sqlDB=lookup.getSQLDB()
        if sqlDB is not None:
            print("testGeoText from database %s " % sqlDB.dbname)
            totalResult=sqlDB.query("""select count(*) as count
  from event_wikicfp
  where locality is not null""")
            total=totalResult[0]['count']
            listOfDicts=sqlDB.query(sqlQuery)
            index=0
            rsum=0
            found=0
            problems=[]
            for record in listOfDicts:
                locality=record['locality']
                count=record['count']
                index+=1
                rsum+=count
                print("%5d: %5d/%5d %5.1f%%=%s" %(index,count,rsum,rsum/total*100,locality))
                geo=GeoText(locality)
                if debug:
                    print("  %s" % geo.countries)
                    print("  %s" % geo.cities)    
                city=geograpy.locateCity(locality)
                if city is not None:
                    found+=1
                else:
                    problems.append(locality)
                if debug:
                    print("  %s%s" % (city,'✅' if city is not None else '❌'))
            if self.debug:        
                print ("found %d/%d = %5.1f%%" % (found,limit,found/limit*100))
                print ("problems: %s" % problems)
            self.assertTrue(found/limit>0.8)
        pass
    
    def testExamples(self):
        examples=[
            'Singapore',
            'Beijing, China',
            'Paris, France',
            'Barcelona, Spain',
            'Rome, Italy',
            'Hong Kong',
            'Bangkok, Thailand',
            'Vienna, Austria',
            'Athens, Greece',
            'Shanghai, China']
        for example in examples:
            geo=GeoText(example)
            print (geo.countries)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()