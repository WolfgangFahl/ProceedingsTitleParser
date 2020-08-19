'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp


class TestDblp(unittest.TestCase):
    '''
    test Dblp handling
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDblp(self):
        ''' test reading dblp data '''
        dblp=Dblp()
        dblp.em.removeCacheFile()
        #EventManager.debug=True
        dblp.cacheEvents()
        foundEvents=len(dblp.rawevents)
        cachedEvents=len(dblp.em.events)
        dblp.em.extractCheckedAcronyms() 
        self.assertEqual(43978,foundEvents)
        self.assertEqual(43978,cachedEvents)
        print("found %d  and cached %d events from dblp" % (foundEvents,cachedEvents))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()