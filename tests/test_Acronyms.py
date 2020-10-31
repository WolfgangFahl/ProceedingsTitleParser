'''
Created on 2020-10-31

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP
from storage.config import StoreMode
from storage.query import Query
import re

class TestAcronyms(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def getWikiCFPDB(self):
        wikiCFP=WikiCFP()
        em=wikiCFP.em
        sqlDB=em.getSQLDB(em.getCacheFile(em.config, StoreMode.SQL))
        return sqlDB
       
    def testAcronyms(self):
        '''
        test Acronyms
        '''
        sqlDB=self.getWikiCFPDB()
        acronymRecords=sqlDB.query("select acronym from event_wikicfp")
        print ("total acronyms: %d" % len(acronymRecords))
        limit=81966
        count=0
        for regex in [r'[A-Z]+\s*[0-9]+']:
            for acronymRecord in acronymRecords[:limit]:
                acronym=acronymRecord['acronym']
                matches=re.match(regex,acronym)
                if matches:
                    count+=1
                print ("%s:%s" % ('✅' if matches else '❌' ,acronym))
            print("%d/%d (%5.1f%%) matches for %s" % (count,limit,count/limit*100,regex)) 

    def testQueries(self):
        '''
        test Queries
        '''
        sqlDB=self.getWikiCFPDB()
        queries=[ 
            {"name":"order of CFPs","query":"select eventId,acronym,year,url from event_wikicfp limit 10"},
            {"name":"cfps per year", "query": """select count(*) as perYear,year 
from event_wikicfp 
group by year
order by 2"""},]
        for query in queries:
            dbQuery=Query(query['name'],query['query'],"sql")
            listOfDicts=sqlDB.query(dbQuery.query)
            markup="=== %s ===\n" % (query['name'])
            markup+=dbQuery.asWikiSourceMarkup()
            markup+=dbQuery.asWikiMarkup(listOfDicts)
            print (markup)
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()