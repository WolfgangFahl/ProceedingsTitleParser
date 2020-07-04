'''
Created on 2020-07-04

@author: wf
'''
import unittest

import time
from ptp.openresearch import OpenResearch
from ptp.event import EventManager

class TestOpenResearch(unittest.TestCase):
    ''' test accessing open research data '''
    debug=False

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
        
    def testOpenResearchCaching(self):
        ''' test caching of open research results '''
        opr=OpenResearch()
        limit=20000
        em=opr.cacheEvents(limit=limit)
        if TestOpenResearch.debug:
            print(em.asJson())
        print("found %d events" % (len(em.events)))
        minexpected=5044
        self.assertTrue(len(em.events)>=minexpected)
        em.store()
        self.assertTrue(EventManager.isCached())
        start_time = time.time()
        em2=EventManager.fromStore()
        print("fromStore took %5.1f s" % (time.time() - start_time))
        self.assertEquals(len(em2.events),len(em.events))
        zeus2018=em2.lookup("ZEUS 2018")
        self.assertTrue(zeus2018 is not None)
        print (zeus2018.asJson())
            
    def testGetEvent(self):
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