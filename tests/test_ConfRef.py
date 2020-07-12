'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.confref import ConfRef
import os
class TestConfRef(unittest.TestCase):
    ''' test handling for data from portal.confref.org '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testConfRef(self):
        ''' test reading confRef data '''
        confRef=ConfRef()
        cacheFile=confRef.em.getCacheFile()
        if os.path.isfile(cacheFile):
            os.remove(cacheFile)
        confRef.cacheEvents()
        foundEvents=len(confRef.rawevents)
        cachedEvents=len(confRef.em.events)
        self.assertEqual(37945,foundEvents)
        self.assertEqual(5704,cachedEvents)
        print("found %d  and cached %d events from confref" % (foundEvents,cachedEvents))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
