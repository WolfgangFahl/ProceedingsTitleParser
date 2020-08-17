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
        self.debug=False
        pass


    def tearDown(self):
        pass

    @staticmethod
    def getJena(mode='query',debug=False,typedLiterals=False):
        '''
        get the jena endpoint for the given mode
        '''
        endpoint="http://localhost:3030/cr"
        jena=Jena(endpoint,mode=mode,debug=debug,typedLiterals=typedLiterals)
        return jena
        
    def testJenaQuery(self):
        '''
        test local jena fuseki endpoint
        '''
        jena=TestJena.getJena()
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
    
    def testJenaInsert(self):
        jena=TestJena.getJena(mode="update")
        insertString = """
        PREFIX cr: <http://cr.bitplan.com/>
        INSERT DATA { 
          cr:version cr:author "Wolfgang Fahl". 
        }
        """
        result=jena.insert(insertString)
        if self.debug:
            print (result)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()