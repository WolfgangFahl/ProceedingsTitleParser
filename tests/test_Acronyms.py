'''
Created on 2020-10-31

@author: wf
'''
import unittest
from ptp.wikicfp import WikiCFP
from lodstorage.storageconfig import StoreMode
from lodstorage.query import Query
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
    
    def showPercentage(self,value,total,title):
        print("%d/%d (%5.1f%%)  %s" % (value,total,value/total*100,title)) 
    
    def getMatchingRecords(self,sqlDB,regex,whereClause,show=10):
        acronymRecords=sqlDB.query("select acronym,startDate from event_wikicfp where %s" % whereClause)
        if show:
            print ("total acronyms for %s: %d" % (whereClause,len(acronymRecords)))
        count=1
        limit=len(acronymRecords)
        matchingRecords=[]
        for acronymRecord in acronymRecords:
            acronym=acronymRecord['acronym']
            matches=re.match(regex,acronym)
            if matches:
                count+=1
                matchingRecords.append(acronymRecord)
            if show and count<show:
                print ("%s:%s" % ('✅' if matches else '❌' ,acronym))
        if show:
            self.showPercentage(count,limit, "matches for %s" % regex)
        return matchingRecords
    
    def checkPattern(self,sqlDB,regex,year,debug=False):
        '''
        check the given regex pattern for the given year
        '''
        self.getMatchingRecords(sqlDB,regex,"year=%d" %year)
       
    def testAcronyms(self):
        '''
        test Acronyms
        '''
        sqlDB=self.getWikiCFPDB()
        for year in range(2007,2021):
            for regex in [r'[A-Z]+\s*[0-9]+']:
                self.checkPattern(sqlDB,regex,year,debug=True)
                
    def testYears(self):
        '''
        test the hypothesis that the year part of the event's acronym correlates
        with the year of the stardate of the event
        '''
        sqlDB=self.getWikiCFPDB()
        regex=r'[A-Z]+\s*[12][0-9]{3}'    
        matchedEvents=self.getMatchingRecords(sqlDB,regex,"year >2006 and year <2022")
        yearDifferent=0
        for matchedEvent in matchedEvents:
            acronym=matchedEvent['acronym']
            startDate=matchedEvent['startDate']
            acronymYear=re.sub(r"^.*([12][0-9]{3}).*$",r"\1", acronym)
            if acronymYear!=str(startDate.year):
                yearDifferent+=1
                #print ("%s:%s != %s" % (acronym,acronymYear,startDate.year))
        self.showPercentage(yearDifferent,len(matchedEvents),"year different")
                   
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