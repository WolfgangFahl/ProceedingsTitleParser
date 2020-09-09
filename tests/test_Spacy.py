'''
Created on 2020-09-07

@author: wf
'''
import unittest
import spacy
import os
from tests.test_WordParser import TestWordParser
from ptp.lookup import Lookup

class TestSpacy(unittest.TestCase):
    '''
    test NLP with spacy 
    
    https://pypi.org/project/spacy/
    '''

    def setUp(self):
        self.debug=False
        path=os.path.dirname(__file__)
        self.titlesdir=path+"/../sampledata/"
        pass


    def tearDown(self):
        pass


    def testSpacy(self):
        '''
        test the space NLP library
        '''
        nlp = spacy.load('en_core_web_sm')
        index=0
        limit=100
        lookup=Lookup("test Spacy")
        sqlDB=lookup.getSQLDB()
        if sqlDB is not None:
            for source in ['wikidata','crossref','dblp','CEUR-WS']:
                listOfDicts=TestWordParser.getProceedingsTitles(sqlDB,source)
                for record in listOfDicts:
                    title=record['title']
                    doc = nlp(title)
                    print ("found %d entities in %s:%s" % (len(doc.ents),record['eventId'],title))
                    for ent in doc.ents:
                        print("  %s(%s)" % (ent,ent.label_))
                    index+=1
                    if index>limit: break
                if index>limit: break
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()