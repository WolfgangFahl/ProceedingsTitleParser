'''
Created on 04.07.2020

@author: wf
'''
import unittest
from titleparser.openresearch import OpenResearch

class TestOpenResearch(unittest.TestCase):
    ''' test accessing open research data '''
    debug=True

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testGetInfo(self):
        ''' get the semantic mediawiki info'''
        opr=OpenResearch()
        result=opr.smw.info()
        if (TestOpenResearch.debug):
            print (result)
        self.assertTrue('info' in result)   
            
    def testGetEvents(self):
        ''' get the events from OpenResearch '''
        opr=OpenResearch()
        event=opr.getEvent("ZEUS 2010")
        self.assertTrue(event is not None)
        if TestOpenResearch.debug:
            print (event)  
            print (event.asJson())
        self.assertEqual("http://www2.informatik.hu-berlin.de/top/zeus/", event.homepage)    
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()