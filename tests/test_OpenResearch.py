'''
Created on 2020-07-04

@author: wf
'''
import unittest

import time
from ptp.openresearch import OpenResearch
from ptp.event import EventManager
from ptp.plot import Plot
import pyparsing as pp

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
        opr=OpenResearch(debug=True)
        em=opr.cacheEvents(limit=20000,batch=2000)
        minexpected=8700
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
    
    def testAcronyms(self):
        ''' get a histogram of acronyms '''
        em=OpenResearch.getEventManager()
        acLenList=[]
        matchCount=0
        acronym4LetterPlusYear=pp.Regex(r'[A-Z]{4} \d{4}')
        for event in em.events.values():
            if event.acronym is not None:
                acLen=len(event.acronym)
                acLenList.append(acLen)
                if acLen==9:
                    try:
                        val=acronym4LetterPlusYear.parseString(event.acronym)
                        matchCount+=1
                    except pp.ParseException as pe:    
                        print (event.acronym)
        plot=Plot(acLenList,"acronym length",debug=True)     
        plot.hist(mode='save')
        print (plot.counter.most_common(10))
        total=len(acLenList)
        print ("matched: %d (%3.1f%%)" % (matchCount,matchCount/2808*100))
        for common in [3,5,7,9,11,13]:
            aclensum=0
            for e in sorted(plot.counter.most_common(common)):
                aclen,acLenCount=e
                print ("%2d: %4d (%3.1f %%)" % (aclen,acLenCount,acLenCount/total*100))
                aclensum=aclensum+acLenCount
            print ("most common %d of %d: %3.1f %%" % (common,total,aclensum/total*100))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()