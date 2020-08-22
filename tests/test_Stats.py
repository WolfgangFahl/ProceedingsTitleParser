'''
Created on 2020-08-18

@author: wf
'''
import unittest
from storage.sparql import SPARQL
from ptp.query import QueryManager

class TestStats(unittest.TestCase):
    '''
    test statistics
    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SPARQL(self):
        qm=QueryManager(debug=True)
        self.assertEqual(2,len(qm.queriesByName))
        endpoint="http://localhost:3030/cr"
        sparql=SPARQL(endpoint)
        for name,query in qm.queriesByName.items():
            markup=query.asWikiMarkup(sparql)
            markup=markup.replace("http://cr.bitplan.com/","https://cr.bitplan.com/index.php/Property:")
            print("== %s ==" % (name))
            print(markup)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_SPARQL']
    unittest.main()