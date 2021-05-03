'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp
from ptp.relevance import Category


class TestDblp(unittest.TestCase):
    '''
    test Dblp handling
    '''
    def setUp(self):
        self.forceCaching=False
        pass

    def tearDown(self):
        pass
    
    def getEvents(self):
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
        return dblp,foundEvents

    def testDblp(self):
        ''' test reading dblp data '''
        dblp,foundEvents=self.getEvents()
        cachedEvents=len(dblp.em.events)
        dblp.em.extractCheckedAcronyms() 
        self.assertTrue(foundEvents>43950)
        self.assertTrue(cachedEvents>43950)
        print("found %d  and cached %d events from dblp" % (foundEvents,cachedEvents))
        pass
        
    def testMostCommonCategories(self):
        '''
        get the most common first letters
        '''
        dblp,foundEvents=self.getEvents()
        self.assertTrue(foundEvents>43950)
        categories=[
            Category("first Letter",lambda event:event.title[0]),
            Category("first Word",lambda event:event.title.split(' ',1)[0])
        ]
        for eventId in dblp.em.events:
            if eventId.startswith("conf"):
                event=dblp.em.events[eventId]
                for category in categories:
                    category.add(event)
        for category in categories:
            print(category.mostCommonTable(tablefmt="mediawiki"))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()