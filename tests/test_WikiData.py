'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.wikidata import WikiData
import os

class TestWikiData(unittest.TestCase):
    ''' test the WikiData proceedings titles source '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testWikiData(self):
        ''' test getting the wikidata information '''
        wd=WikiData(debug=True)
        cacheFile=wd.em.getCacheFile()
        if os.path.isfile(cacheFile):
            os.remove(cacheFile)
        wd.cacheEvents()
        print("found %d wikidata events" % (len(wd.em.events)))
        self.assertTrue(len(wd.em.events)>310)
        size=os.stat(cacheFile).st_size
        print (size)
        self.assertTrue(size>208000)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
