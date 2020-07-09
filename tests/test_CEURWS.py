'''
Created on 2020-07-06

@author: wf
'''
import unittest
import os
from ptp.ceurws import CEURWS

class TestCEURWS(unittest.TestCase):
    ''' test handling proceeding titles retrieved
    from http://ceur-ws.org/ Volumes '''


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCEURWS(self):
        ''' test CEUR-WS cache handling'''
        cw=CEURWS(debug=False)
        cacheFile=cw.em.getCacheFile()
        if os.path.isfile(cacheFile):
            os.remove(cacheFile)
        cw.cacheEvents()
        print(len(cw.em.events))
        self.assertTrue(len(cw.em.events)>940)
        size=os.stat(cacheFile).st_size
        print (size)
        self.assertTrue(size>500000)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()