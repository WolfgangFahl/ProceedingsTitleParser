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
        self.forceCaching=False
        pass

    def tearDown(self):
        pass

    def testDblp(self):
        ''' test reading dblp data '''
        dblp=Dblp()
        if self.forceCaching:
            dblp.em.removeCacheFile()
        #EventManager.debug=True
        if not dblp.em.isCached():
            dblp.cacheEvents()
            foundEvents=len(dblp.rawevents)
        else:
            dblp.em.fromStore()
            foundEvents=len(dblp.em.events)
        cachedEvents=len(dblp.em.events)
        dblp.em.extractCheckedAcronyms() 
        self.assertTrue(foundEvents>43950)
        self.assertTrue(cachedEvents>43950)
        print("found %d  and cached %d events from dblp" % (foundEvents,cachedEvents))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()