'''
Created on 2020-09-03

@author: wf
'''
import unittest
from ptp.ontology import Ontology
import getpass
import json

class TestOntology(unittest.TestCase):
    ''' 
    test the Ontology access via Requirements Wiki
    '''

    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testOntology(self):
        '''
        test reading the ontology from the RQ wiki
        '''
        if getpass.getuser()!="travis":
            o=Ontology(debug=self.debug)
            schemaManager=o.getSchemaProperties('rq')
            if self.debug:
                schemas=schemaManager.schemasByName.values()
                print("found %d schemas" % len(schemas))
                for schema in schemas:
                    print("= %s =" % schema.name)
                    print("found %d properties for %s" % (len(schema.propsById),schema.name))
                    print("<source lang='json'>%s</source>" % json.dumps(schema, default=lambda o: o.__dict__, indent=2))
            self.assertTrue(len(schemas)>8)    
            allProps=schemaManager.allProperties()
            schemaManager.store(allProps,sampleRecordCount=len(allProps))
            self.assertTrue(schemaManager.isCached())
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()