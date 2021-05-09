'''
Created on 2020-07-17

@author: wf
'''
import unittest
from ptp.dblp import Dblp
from ptp.relevance import Tokenizer, TokenSequence
from ptp.signature import RegexpCategory,OrdinalCategory, EnumCategory, ParsingCategory
from pyparsing import oneOf

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
    
    def testTokenizer(self):
        tokenizer=Tokenizer([OrdinalCategory()])
        event={
            'eventId':'conf/icwe/icwe2019',
            'acronym':'ICWE 2019',
            'title':'Web Engineering - 19th International Conference, ICWE 2019, Daejeon, South Korea, June 11-14, 2019, Proceedings'
        }
        tokenSequence=tokenizer.tokenize(event['title'], event)
        self.assertEqual(1,len(tokenSequence.matchResults))
        token=tokenSequence.matchResults[0]
        self.assertEqual('Ordinal',token.category.name)
        self.assertEqual("19th",token.tokenStr)
        self.assertEqual(3,token.pos)
        self.assertEqual(19,token.value)
    
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
            EnumCategory('syntax'),
            ParsingCategory('part',"Part"+oneOf("A B C 1 2 3 4 I II III IV")+".")
        ]
        tokenizer=Tokenizer(categories)
        tokenSequences={}
        for eventId in dblp.em.events:
            if eventId.startswith("conf"):
                event=dblp.em.events[eventId]
                tokenSequences[eventId]=tokenizer.tokenize(event.title,event)
        limit=50
        count=0
        for tokenSequence in tokenSequences.values():
            for token in tokenSequence.matchResults:
                count+=1
                if count>limit:
                    break;
                print(token)
        for category in categories:
            print(f"=== {category.name} ===")
            print(category.mostCommonTable(tablefmt="mediawiki"))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()