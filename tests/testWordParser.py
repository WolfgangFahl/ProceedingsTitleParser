'''
Created on 2020-09-04

@author: wf
'''
import unittest
from ptp.wordparser import CorpusWordParser
from ptp.lookup import Lookup
from storage.sql import SQLDB
import os
import pandas as pd
from pandas import DataFrame

class TestWordParser(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testWordParser(self):
        '''
        try finding quantiles
        
        see https://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy
        '''
        dbFile=Lookup.getDBFile()
        if os.path.isfile(dbFile):
            sqlDB=SQLDB(dbFile)
            sqlQuery="""select source,title
from event 
where title like '%Proceedings of%'
and source in ('wikidata')
            """
            listOfDicts=sqlDB.query(sqlQuery)
            cwp=CorpusWordParser()
            lens=cwp.parse(listOfDicts)
            df=DataFrame(lens)
            print (df.quantile(1))
            quantileValues=df.quantile(.90)
            print(quantileValues);
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()