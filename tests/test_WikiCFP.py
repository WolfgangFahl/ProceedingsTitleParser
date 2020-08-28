'''
Created on 2020-08-20

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP, WikiCFPEvent
import os
from pathlib import Path

class TestWikiCFP(unittest.TestCase):
    '''
    test events from WikiCFP
    '''

    def setUp(self):
        self.debug=False
        self.profile=False
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
        self.assertTrue(wikiCFP.em.isCached())
        self.assertTrue(len(wikiCFP.em.events)>60000)
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
    
    def testEventScraping(self):
        '''
        test scraping the given event
        '''
        eventIds=[3862]
        event=WikiCFPEvent(debug=True)
        for eventId in eventIds:
            rawEvent=event.fromEventId(eventId)
            print (rawEvent)
            
    def testCrawlEvents(self):
        '''
        test crawling a few events and storing the result to a json file
        '''
        wikiCFP=WikiCFP()
        jsonFilePath=wikiCFP.crawl(0, 3860, 3869)
        size=os.stat(jsonFilePath).st_size
        print ("JSON file has size %d" % size)
        self.assertTrue(size>5000)
        batchEm=wikiCFP.getEventManager(self.debug, self.profile, 'json')
        batchEm.fromStore(cacheFile=jsonFilePath)
        self.assertEqual(len(batchEm.events.values()),10)
        inspect=True
        if inspect:
            tmpPath="/tmp/%s" % os.path.basename(jsonFilePath)
            Path(jsonFilePath).rename(tmpPath)
                

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()