'''
Created on 2020-08-30

@author: wf
'''
import unittest
from ptp.lookup import Lookup
from ptp.ontology import Ontology
from storage.sql import SQLDB
import getpass


class TestLookup(unittest.TestCase):
    '''
    test Lookup - the combined  lookup access to events from all active sources
    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLookup(self):
        '''
        test the number of sources and storing to "Event_all"
        '''
        if getpass.getuser()!="travis":
            lookup=Lookup("test")
            self.assertEqual(7,len(lookup.ems))
            errors=lookup.store('Event_all')
            self.assertEqual(0,len(errors))
            lookup.createView()
        pass
    
    def testCreateEventAll(self):
        '''
        check that the eventall database is created correctly
        '''
        withWikiData=getpass.getuser()!="travis"
        lookup=Lookup("CreateEventAll")
        self.assertEqual(7,len(lookup.ems))
        sqlDB=lookup.createEventAll(maxAgeMin=1,withWikiData=withWikiData)
        tableList=sqlDB.getTableList()
        print(tableList)
        self.assertTrue(len(tableList)>7)
    
    def testPlantUml(self):
        '''
        get plant UML functionality 
        '''
        o=Ontology()
        schemaManager=o.getRQSchema()  # set fromCache=false to force SMW query
        
        lookup=Lookup("plantuml",getAll=False,butNot='or')
        dbfile=lookup.getDBFile('Event_all')
        sqlDb=SQLDB(dbfile)
        tableList=sqlDb.getTableList()
        for table in tableList:
            if not table['name'].startswith("Event_"):
                tableList.remove(table)
        plantUml=SQLDB.tableListToPlantUml(tableList, 'DataDonations',generalizeTo="Event")
        print(plantUml)
        self.assertTrue("Event <|-- Event_confref" in plantUml)
        self.assertTrue("entity Event {" in plantUml)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()