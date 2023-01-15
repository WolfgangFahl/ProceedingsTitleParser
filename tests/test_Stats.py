'''
Created on 2020-08-18

@author: wf
'''
import unittest
from lodstorage.sparql import SPARQL
from lodstorage.query import QueryManager
from ptp.lookup import Lookup
import os

class TestStats(unittest.TestCase):
    '''
    test statistics via Query manager
    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def getQueryManager(self):
        path=os.path.dirname(__file__)+"/.."
        qm=QueryManager(lang='sql',debug=self.debug,path=path)
        return qm
    
    def test_SQL(self):
        '''
        test SQL queries
        '''
        qm=self.getQueryManager()
        self.assertEqual(17,len(qm.queriesByName))
        lookup=Lookup.ensureAllIsAvailable()
        sqlDB=lookup.getSQLDB()
        for name,query in qm.queriesByName.items():
            listOfDicts=sqlDB.query(query.query)
            markup=query.asWikiMarkup(listOfDicts)
            print("== %s ==" % (name))
            print("=== query ===")
            print (query.asWikiSourceMarkup())
            print("=== result ===")
            print(markup)
        

    def test_SPARQL(self):
        '''
        test SPARQL queries
        '''
        # disable test for the time being
        return
        qm=self.getQueryManager()
        self.assertEqual(4,len(qm.queriesByName))
        endpoint="http://localhost:3030/cr"
        sparql=SPARQL(endpoint)
        for name,query in qm.queriesByName.items():
            listOfDicts=sparql.queryAsListOfDicts(query.query)
            markup=query.asWikiMarkup(listOfDicts)
            markup=markup.replace("http://cr.bitplan.com/","https://cr.bitplan.com/index.php/Property:")
            print("== %s ==" % (name))
            print("=== query ===")
            print (query.asWikiSourceMarkup())
            print("=== result ===")
            print(markup)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_SPARQL']
    unittest.main()
