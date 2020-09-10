'''
Created on 2020-08-30

@author: wf
'''
import unittest
from ptp.lookup import Lookup
from ptp.ontology import Ontology
from lodstorage.sql import SQLDB
from lodstorage.uml import UML
import getpass
from datetime import datetime


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
        check that the event all database is created correctly
        '''
        withWikiData=getpass.getuser()!="travis"
        lookup=Lookup("CreateEventAll")
        self.assertEqual(7,len(lookup.ems))
        errors=lookup.check(lookup.getSQLDB(),debug=True)
        if len(errors)>0:
            print (errors)
            sqlDB=lookup.createEventAll(maxAgeMin=0,withWikiData=withWikiData)
            errors=lookup.check(sqlDB,debug=True)
        if len(errors)>0:
            self.assertEqual(0,len(errors))
    
    def testPlantUml(self):
        '''
        get plant UML functionality 
        '''
        schemaManager=None
        if getpass.getuser()!="travis":
            o=Ontology()
            schemaManager=o.getRQSchema(fromCache=False) # to force SMW query
        
        lookup=Lookup("plantuml",getAll=False,butNot='or')
        dbfile=lookup.getDBFile('Event_all')
        sqlDB=SQLDB(dbfile)
        tableList=sqlDB.getTableList()
        eventTableList=[]
        eventSchemas=lookup.getEventSchemas()
        for table in tableList:
            tableName=table['name']
            if tableName.startswith("Event_"):
                table['schema']=eventSchemas[tableName]
                eventTableList.append(table)
                countQuery="SELECT count(*) as count from %s" % tableName
                countResult=sqlDB.query(countQuery)
                table['instances']=countResult[0]['count']
        self.assertEqual(7,len(eventTableList))        
        uml=UML()
        now=datetime.now()
        nowYMD=now.strftime("%Y-%m-%d")
        title="""ConfIDent  Entities
%s
[[https://projects.tib.eu/en/confident/ © 2019-2020 ConfIDent project]]
see also [[http://ptp.bitplan.com/settings Proceedings Title Parser]]
""" %nowYMD
        plantUml=uml.mergeSchema(schemaManager,eventTableList,title=title,packageName='DataDonations',generalizeTo="Event")
        print(plantUml)
        self.assertTrue("Event <|-- Event_confref" in plantUml)
        self.assertTrue("class Event " in plantUml)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()