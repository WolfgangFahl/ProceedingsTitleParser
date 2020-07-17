'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp


class TestDblp(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDblp(self):
        ''' test reading confRef data '''
        dblp=Dblp()
        dblp.em.removeCacheFile()
        #EventManager.debug=True
        dblp.cacheEvents()
        foundEvents=len(dblp.rawevents)
        cachedEvents=len(dblp.em.events)
        dblp.em.extractAcronyms() 
        self.assertEqual(43978,foundEvents)
        self.assertEqual(43978,cachedEvents)
        print("found %d  and cached %d events from dblp" % (foundEvents,cachedEvents))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()