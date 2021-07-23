'''
Created on 2020-07-04

@author: wf
'''
import unittest

from ptp.openresearch import OpenResearch
from lodstorage.plot import Plot
import pyparsing as pp
from tests.test_PyParsing import TestPyParsing
from lodstorage.storageconfig import StorageConfig

class TestOpenResearch(unittest.TestCase):
    ''' test accessing open research data '''

    def setUp(self):
        self.debug=False
        pass

    def tearDown(self):
        pass
    
    def testCreateWikiUser(self):
        '''
        test creating a wiki user
        '''
        wikiUser=OpenResearch.createWikiUser()
        self.assertTrue(wikiUser is not None)
        

    def testGetInfo(self):
        ''' get the semantic mediawiki info'''
        opr=OpenResearch()
        result=opr.smw.info()
        if (self.debug):
            print (result)
        self.assertTrue('info' in result)  
        
    def testOpenResearchCaching(self):
        ''' test caching of open research results '''
        config=StorageConfig.getDefault(self.debug)
        opr=OpenResearch(config=config)
        # only cache if not cached yet
        if not opr.em.isCached():
            opr.cacheEvents(opr.em,limit=20000,batch=2000)
            minexpected=8500
            self.assertTrue(len(opr.em.events)>=minexpected)
            opr.em.store()
        else:
            opr.em.fromStore()    
        self.assertTrue(opr.em.isCached())
      
        opr2=OpenResearch()
        opr2.em.fromStore()
        self.assertEqual(len(opr2.em.events),len(opr.em.events))
        events=opr2.em.lookup("ZEUS 2018")
        self.assertEqual(1,len(events))
        zeus2018=events[0]
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
    
    def testExtractAcronyms(self):
        ''' test acronym extraction from openresearch '''
        opr=OpenResearch()
        opr.initEventManager()
        found=len(opr.em.eventsByAcronym)
        print ("found %d acronyms" % (found))
        expected=3000
        self.assertTrue(found>=expected)        
        
    
    def testAcronymStructure(self):
        ''' get a histogram of acronyms '''
        opr=OpenResearch()
        opr.initEventManager()
        acLenList=[]
        grammars={
            '  with 4digit year': pp.Regex(r'^.{0,10}(19|20)[0-9][0-9].{0,10}$'),
            '      4 UpperCase+blank+4Year Digits'  : pp.Regex(r'^[A-Z]{4} \d{4}$'),
            '    2-3 UpperCase+blank+4Year Digits'  : pp.Regex(r'^[A-Z]{2,3} \d{4}$'),
            '    2-7 UpperCase+blank or dash+2-4 Digits': pp.Regex(r'^[A-Z]{2,7}[ -]+\d{2,4}$'),
            'nth 4-6 Uppercase 20##': pp.Regex(r'^(([1-9][0-9]?)th\s)?[A-Z]{4,6}\s20[0-9][0-9]$'),
            ' full monty': pp.Regex(r'^(([1-9][0-9]?)th\s)?[A-Z/_-]{2,10}[ -]*(19|20)[0-9][0-9]$') 
            }
        examples=[]
        for event in opr.em.events.values():
            if hasattr(event, 'acronym'):
                if event.acronym is not None:
                    acLen=len(event.acronym)
                    acLenList.append(acLen)
                    examples.append(event.acronym)
        plot=Plot(acLenList,"acronym length",debug=True)     
        plot.hist(mode='save')
        print (plot.counter.most_common(10))
        total=len(acLenList)
        for common in [3,5,7,9,11,13]:
            aclensum=0
            for e in sorted(plot.counter.most_common(common)):
                aclen,acLenCount=e
                print ("%2d: %4d (%3.1f %%)" % (aclen,acLenCount,acLenCount/total*100))
                aclensum=aclensum+acLenCount
            print ("most common %d of %d: %3.1f %%" % (common,total,aclensum/total*100))
            
        TestPyParsing.doTestGrammars(examples, grammars)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()