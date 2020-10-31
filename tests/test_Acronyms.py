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
    
    def checkPattern(self,sqlDB,regex,year,debug=False):
        '''
        check the given regex pattern for the given year
        '''
        acronymRecords=sqlDB.query("select acronym from event_wikicfp where year=%d" % year)
        print ("total acronyms for year %d: %d" % (year,len(acronymRecords)))
        count=1
        limit=len(acronymRecords)
        for acronymRecord in acronymRecords:
            acronym=acronymRecord['acronym']
            matches=re.match(regex,acronym)
            if matches:
                count+=1
            if debug and count<10:
                print ("%s:%s" % ('✅' if matches else '❌' ,acronym))
        print("%d/%d (%5.1f%%) matches for %s" % (count,limit,count/limit*100,regex)) 
   
       
    def testAcronyms(self):
        '''
        test Acronyms
        '''
        sqlDB=self.getWikiCFPDB()
        for year in range(2007,2021):
            for regex in [r'[A-Z]+\s*[0-9]+']:
                self.checkPattern(sqlDB,regex,year,debug=True)
      
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