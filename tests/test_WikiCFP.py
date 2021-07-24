'''
Created on 2020-08-20

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP, WikiCFPEventFetcher
import os
from pathlib import Path
from collections import Counter

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

    def printDelimiterCount(self,names):
        '''
        print the count of the most common use delimiters in the given name list
        '''
        ordC=Counter()
        for name in names:
            if name is not None:
                for char in name:
                    code=ord(char)
                    if code<ord("A"):
                        ordC[code]+=1
        for index,countT in enumerate(ordC.most_common(10)):
            code,count=countT
            print ("%d: %d %s -> %d" % (index,code,chr(code),count))

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
        wikiCFP=WikiCFP()
        if not wikiCFP.em.isCached():
            wikiCFP.cacheEvents()
        else:
            wikiCFP.em.fromStore()
        self.assertTrue(wikiCFP.em.isCached())
        self.assertTrue(len(wikiCFP.em.events)>80000)
        names=[]
        for event in wikiCFP.em.events.values():
            names.append(event.locality)
        self.printDelimiterCount(names)

        pass

    def testInvalidUrl(self):
        '''
        make sure only valid urls are accepted
        '''
        event=WikiCFPEventFetcher(debug=True)
        try:
            event.fromUrl("http://google.com")
            self.fail("invalid url should raise an exception")
        except:
            pass

    def testEventScraping(self):
        '''
        test scraping the given event

         test "This item has been deleted" WikiCFP items
        e.g.
        http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=3
        '''
        eventIds=[3862,1]
        isDeleted=[False,True]
        event=WikiCFPEventFetcher(debug=self.debug)
        for index,eventId in enumerate(eventIds):
            rawEvent=event.fromEventId(eventId)
            if self.debug:
                print (rawEvent)
            self.assertTrue(isDeleted[index]==rawEvent['deleted'])
            
    def testGettingEventSeriesForEvent(self):
        '''
        test extracting the event series id from th event page
        '''
        self.debug=True
        expectedSeriesId=['1769',None]
        eventIds=[1974,139964]
        event=WikiCFPEventFetcher(debug=self.debug)
        for index,eventId in enumerate(eventIds):
            rawEvent=event.fromEventId(eventId)
            expected=expectedSeriesId[index]
            if expected:
                self.assertEqual(expected,rawEvent['seriesId'])
            else:
                self.assertTrue('seriesId' not in rawEvent)
            if self.debug:
                print (f"{index}:{rawEvent}")
            
    def testGettingLatestEvent(self):
        '''
        get the latest event Id with a binary search
        '''
        #latestEvent=WikiCFPEventFetcher.getLatestEvent(showProgress=True)
        pass

    def testCrawlEvents(self):
        '''
        test crawling a few events and storing the result to a json file
        '''
        wikiCFP=WikiCFP()
        jsonFilePath=wikiCFP.crawl(0, 1, 10)
        size=os.stat(jsonFilePath).st_size
        print ("JSON file has size %d" % size)
        self.assertTrue(size>5000)
        batchEm=wikiCFP.getEventManager(mode='json')
        batchEm.fromStore(cacheFile=jsonFilePath)
        self.assertEqual(len(batchEm.events.values()),10)
        inspect=False # if setting to True make sure tmp is on same filesystem
        # see https://stackoverflow.com/questions/42392600/oserror-errno-18-invalid-cross-device-link
        if inspect:
            tmpPath="/tmp/%s" % os.path.basename(jsonFilePath)
            Path(jsonFilePath).rename(tmpPath)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
