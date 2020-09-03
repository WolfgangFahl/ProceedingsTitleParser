'''
Created on 2020-09-03

@author: wf
'''
import unittest
from ptp.ontology import Ontology
import getpass
from storage.jsonable import JSONAble

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
                    print("<source lang='json'>%s</source>" % schema.toJSON())
            self.assertTrue(len(schemas)>8)    
            allProps=schemaManager.allProperties()
            schemaManager.store(allProps,sampleRecordCount=len(allProps))
            self.assertTrue(schemaManager.isCached())
        pass
    
    def testJsonAble(self):
        family=Family("The Flintstones")
        family.add(Person("Fred","Flintstone")) 
        family.add(Person("Wilma","Flintstone"))
        json1=family.toJSON()
        json2=family.asJSON()
        print(json1)
        print(json2)
             
class Family(JSONAble):
    def __init__(self,name):
        self.name=name
        self.members={}
    
    def add(self,person):
        self.members[person.lastName+","+person.firstName]=person

class Person(JSONAble):
    def __init__(self,firstName,lastName):
        self.firstName=firstName;
        self.lastName=lastName;
  
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()