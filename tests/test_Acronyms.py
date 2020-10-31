'''
Created on 2020-10-31

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP
from storage.config import StoreMode
import re
class TestAcronyms(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testAcronyms(self):
        '''
        test Acronyms
        '''
        wikiCFP=WikiCFP()
        em=wikiCFP.em
        sqlDB=em.getSQLDB(em.getCacheFile(em.config, StoreMode.SQL))
        acronymRecords=sqlDB.query("select acronym from event_wikicfp")
        print ("total acronyms: %d" % len(acronymRecords))
        limit=81966
        count=0
        for regex in [r'[A-Z]+\s*[0-9]+']:
            for acronymRecord in acronymRecords[:limit]:
                acronym=acronymRecord['acronym']
                matches=re.match(regex,acronym)
                if matches:
                    count+=1
                print ("%s:%s" % ('✅' if matches else '❌' ,acronym))
            print("%d/%d (%5.1f%%) matches for %s" % (count,limit,count/limit*100,regex)) 


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()