'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp
from ptp.relevance import Category, Categorizer, TokenSequence
from ptp.signature import RegexpCategory,OrdinalCategory, EnumCategory

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
    
    def testCategorizer(self):
        cat=Categorizer([OrdinalCategory()])
        event={
            'eventId':'conf/icwe/icwe2019',
            'acronym':'ICWE 2019',
            'title':'Web Engineering - 19th International Conference, ICWE 2019, Daejeon, South Korea, June 11-14, 2019, Proceedings'
        }
        results=cat.categorize(event['title'], event)
        self.assertEqual(1,len(results))
        token,pos,value=results['Ordinal'].matchResult[0]
        self.assertEqual("19th",token)
        self.assertEqual(3,pos)
        self.assertEqual(19,value)
    
    def testCategories(self):
        '''
        check some categories 
        '''
        ocat=OrdinalCategory()
        self.assertEqual(745,len(ocat.lookupByKey))
        mcat=EnumCategory("month")
        self.assertEqual(12,len(mcat.lookupByKey))
        
    def testMostCommonCategories(self):
        '''
        get the most common first letters
        '''
        dblp,foundEvents=self.getEvents()
        self.assertTrue(foundEvents>43950)
        categories=[
            RegexpCategory("first Letter",lambda word:word[0] if word else '',r".*"),
            RegexpCategory("word",lambda word:word,r".*"),
            # TODO: country, region, city
            OrdinalCategory(),
            # TODO: year
            EnumCategory('month'),
            EnumCategory('delimiter'),
            EnumCategory('eventType'),
            EnumCategory('extract'),
            EnumCategory('field'),
            EnumCategory('frequency'),
            EnumCategory('organization'),
            EnumCategory('publish'),
            EnumCategory('scope'),
            EnumCategory('syntax')
        ]
        cat=Categorizer(categories)
        categorizations={}
        for eventId in dblp.em.events:
            if eventId.startswith("conf"):
                event=dblp.em.events[eventId]
                categorizations[eventId]=cat.categorize(event.title,event)
        limit=50
        count=0
        for clist in categorizations.values():
            for c in clist.values():
                count+=1
                if count>limit:
                    break;
                print(c)
        for category in categories:
            print(f"=== {category.name} ===")
            print(category.mostCommonTable(tablefmt="mediawiki"))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()