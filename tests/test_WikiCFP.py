'''
Created on 2020-08-20

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP, WikiCFPEvent

class TestWikiCFP(unittest.TestCase):
    '''
    test events from WikiCFP
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testCrawledJsonFiles(self):
        '''
        get the crawl files
        '''
        wikiCFP=WikiCFP()
        crawlFiles=wikiCFP.jsonFiles()
        print ("found %d wikiCFP crawl files" % len(crawlFiles))
        self.assertTrue(len(crawlFiles)>=70)

    def testWikiCFP(self):
        '''
        test event handling from WikiCFP
        '''
        wikiCFP=WikiCFP(debug=False,profile=True)
        if not wikiCFP.em.isCached():
            wikiCFP.cacheEvents()
        else:
            wikiCFP.em.fromStore()    
        #self.assertTrue(wikiCFP.em.isCached())
        #self.assertTrue(len(wikiCFP.em.events)>100)
        pass
    
    def testInvalidUrl(self):
        '''
        make sure only valid urls are accepted
        '''
        event=WikiCFPEvent(debug=True)
        try:
            event.fromUrl("http://google.com")
            self.fail("invalid url should raise an exception")
        except:
            pass
    
    def testEvents(self):
        '''
        test crawling th given events
        '''
        eventIds=[3862]
        event=WikiCFPEvent(debug=True)
        for eventId in eventIds:
            rawEvent=event.fromEventId(eventId)
            print (rawEvent)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()