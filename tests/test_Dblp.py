'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp
from collections import Counter
import numpy
import pandas as pd


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
    
    def testMostCommonFirstLetter(self):
        '''
        get the most common first letters
        '''
        dblp,foundEvents=self.getEvents()
        self.assertTrue(foundEvents>43950)
        # collect first letters
        counter=Counter()
        total=0
        for eventId in dblp.em.events:
            if eventId.startswith("conf"):
                event=dblp.em.events[eventId]
                first=ord(event.title[0])
                counter[first]+=1
                total+=1
        bins=len(counter.keys())
        print(f"found {bins} different first letters in {total} titles")
        for o,count in counter.most_common(bins):
            c=chr(o)
            print (f"{c}: {count:5} {count/total*100:4.1f} %")
        
        
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()