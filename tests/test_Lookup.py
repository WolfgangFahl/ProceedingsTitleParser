'''
Created on 2020-08-30

@author: wf
'''
import unittest
from ptp.lookup import Lookup
from ptp.ontology import Ontology
from storage.sql import SQLDB
from storage.uml import UML
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
        if getpass.getuser()!="travis":
            o=Ontology()
            schemaManager=o.getRQSchema(fromCache=False) # to force SMW query
        
        lookup=Lookup("plantuml",getAll=False,butNot='or')
        dbfile=lookup.getDBFile('Event_all')
        sqlDb=SQLDB(dbfile)
        tableList=sqlDb.getTableList()
        eventTableList=[]
        tableSchemas={
            'Event_or': 'Open Research Entities',
            'Event_CEURWS':'PTP',
            'Event_crossref':'Crossref',
            'Event_confref':'Confref',
            'Event_wikicfp':'WikiCFP',
            'Event_wikidata':'PTP',
            'Event_dblp':'DBLP'}
        for table in tableList:
            tableName=table['name']
            if tableName.startswith("Event_"):
                table['schema']=tableSchemas[tableName]
                eventTableList.append(table)
        self.assertEqual(7,len(eventTableList))        
        uml=UML(debug=True)
        plantUml=uml.mergeSchema(schemaManager,eventTableList,'DataDonations',generalizeTo="Event")
        print(plantUml)
        self.assertTrue("Event <|-- Event_confref" in plantUml)
        self.assertTrue("class Event " in plantUml)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()