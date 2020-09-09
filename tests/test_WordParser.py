'''
Created on 2020-09-04

@author: wf
'''
import unittest
from ptp.wordparser import CorpusWordParser, WordParser, WordUsage
from ptp.lookup import Lookup
from storage.sql import SQLDB
import os
from ptp.plot import Plot
import pandas as pd
from pandas import DataFrame

class TestWordParser(unittest.TestCase):


    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass

    def testWordUsage(self):
        '''
        test the word usage returned by the word parser
        e.g. proper splitting by different separators
        '''
        title='Proceedings of the First International Conference on Phylogenomics. March 15-19, 2006. Quebec, Canada'
        wordparser=WordParser('wikidata','Q21283902')
        wus=wordparser.parse(title)
        for index,wu in enumerate(wus):
            if self.debug:
                print("%2d:%s" % (index,wu.__dict__))
        self.assertEqual(14,len(wus))  
    
    @staticmethod
    def getProceedingsTitles(sqlDB,source):
        sqlQuery="""select source,eventId,title
    from event 
    where title like '%%Proceedings of%%'
    and source in ('%s')
                """ % source
        listOfDicts=sqlDB.query(sqlQuery)
        return listOfDicts        
    
    def testWordParser(self):
        '''
        try finding quantiles
        
        see https://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy
        '''
        lookup=Lookup("test Word parser")
        sqlDB=lookup.getSQLDB()
        if sqlDB is not None:
            totalWordUsages=[]
            for source in ['wikidata','crossref','dblp','CEUR-WS']:
                listOfDicts=TestWordParser.getProceedingsTitles(sqlDB,source)
                cwp=CorpusWordParser()
                wordusages=cwp.parse(listOfDicts)
                lens={}
                for wordusage in wordusages:
                    totalWordUsages.append(wordusage.__dict__)
                    if wordusage.eventId in lens:
                        lens[wordusage.eventId]+=1
                    else:
                        lens[wordusage.eventId]=1    
                df=DataFrame(lens.values())
                print (df.quantile(1))
                quantileValues=df.quantile(.90)
                print(quantileValues);
                plot=Plot(lens.values(),"%s wordcount histogram" %source,xlabel="wordcount",ylabel="frequency")
                plot.hist(mode='save') 
            wordUsageDBFile=Lookup.getDBFile("wordusage")
            wSQLDB=SQLDB(wordUsageDBFile)
            entityInfo=wSQLDB.createTable(totalWordUsages, "wordusage",withDrop=True)
            wSQLDB.store(totalWordUsages, entityInfo)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()