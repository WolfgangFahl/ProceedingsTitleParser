'''
Created on 2020-09-04

@author: wf
'''
import unittest
from ptp.wordparser import CorpusWordParser, WordParser
from ptp.lookup import Lookup
from lodstorage.sql import SQLDB
from lodstorage.uml import UML
from ptp.plot import Plot
from pandas import DataFrame
from datetime import datetime
import os
from collections import Counter

class TestWordParser(unittest.TestCase):
    '''
    test the Word usage based parser
    '''


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
        self.assertEqual(27,len(wus))  
    
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
            
    def getWordUsageDB(self):
        '''
        get the Word usage database
        '''
        wordUsageDBFile=Lookup.getDBFile("wordusage")
        if os.path.isfile(wordUsageDBFile):
            wSQLDB=SQLDB(wordUsageDBFile)
            return wSQLDB
        return None
            
    def testWordUsageTagging(self):
        wSQLDB=self.getWordUsageDB()
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")
        title="""WordUsage  Entities
%s
[[https://projects.tib.eu/en/confident/ © 2020 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
""" %nowYMD
        tableList=wSQLDB.getTableList()
        plantUml=uml.tableListToPlantUml(tableList,title=title, packageName="ptp")
        print (plantUml)
         
            
    def testDelimiters(self):
        '''
        test frequency of delimiter usage
        '''
        wSQLDB=self.getWordUsageDB()
        delimiters=[' ',',','+',':',';','(',')','{','}','[',']','<','>','"',"''",'/','*','\%','&','#','~']
        countResults={}
        totalQuery="select count(distinct(eventId)) as count from wordusage"
        totalResult=wSQLDB.query(totalQuery)
        total=totalResult[0]['count']
        for delimiter in delimiters:
            sqlQuery="select count(*) as count from wordusage where word like '%s%%'" % (delimiter)
            countResult=wSQLDB.query(sqlQuery)
            foundCount=countResult[0]['count']
            countResults[delimiter]=foundCount
        counts=Counter(countResults)
        print (total)
        for delim,count in counts.most_common():
            print ("%s & %7d & %5.3f \\" % (delim,count,count/total))        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()