'''
Created on 2020-07-17

@author: wf
'''
import unittest
from tests.basetest import Basetest
from ptp.relevance import Tokenizer, TokenSequence
from ptp.signature import RegexpCategory,OrdinalCategory, EnumCategory, ParsingCategory
from pyparsing import oneOf

class TestDblp(Basetest):
    '''
    test Dblp handling
    '''
    
    @classmethod
    def setUpClass(cls):
        lookupIds=["dblp"]
        super().setUpClass(lookupIds=lookupIds)
        
    def setUp(self):
        Basetest.setUp(self)
        pass
    
    def getEventManager(self):
        '''
        get DBLP events
        '''
        self.dblpDataSource=self.lookup.getDataSource("dblp")
        return self.dblpDataSource.eventManager
        

    def testDblp(self):
        ''' test reading dblp data '''
        em=self.getEventManager()
        cachedEvents=len(em.events)
        self.assertTrue(cachedEvents>43950)
        if self.debug:
            print(f"found {len(em.events)} cached events from dblp")
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
        em=self.getEventManager()
        self.assertTrue(len(em.events)>43950)
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
        for event in em.events:
            eventId=event.eventId
            if eventId.startswith("conf"):
                tokenSequences[eventId]=tokenizer.tokenize(event.title,event)
        limit=50
        count=0
        for tokenSequence in tokenSequences.values():
            for token in tokenSequence.matchResults:
                count+=1
                if count>limit:
                    break;
                print(token)
        show=False
        if show:
            for category in categories:
                print(f"=== {category.name} ===")
                print(category.mostCommonTable(tablefmt="mediawiki"))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()