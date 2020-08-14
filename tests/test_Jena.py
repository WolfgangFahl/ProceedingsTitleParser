'''
Created on 2020-08-14

@author: wf
'''
import unittest
from storage.jena import Jena

class TestJena(unittest.TestCase):
    '''
    test Apache Jena SPARQL access
    '''

    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testJena(self):
        '''
        test local jena fuseki endpoint
        '''
        endpoint="http://localhost:3030/cr"
        jena=Jena(endpoint)
        queryString = """
        PREFIX cr: <http://cr.bitplan.com/>
        SELECT ?version WHERE { cr:version cr:version ?version. }
        """
        
        results=jena.query(queryString)
        if self.debug:     
            print (results)
   
        self.assertEqual(1,len(results))
        result=results[0]
        self.assertTrue("version" in result)
        version=result["version"]
        self.assertEqual("literal",version['type'])
        self.assertEqual("0.0.1",version['value'])
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()