'''
Created on 2020-07-25

@author: wf
'''
import unittest
from ptp.crossref import Crossref
from ptp.event import Event

class TestCrossref(unittest.TestCase):
    '''
    import data from Crossref
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def testFixUmlauts(self):
        '''
        workaround Umlaut issue see https://stackoverflow.com/questions/63486767/how-can-i-get-the-fuseki-api-via-sparqlwrapper-to-properly-report-a-detailed-err
        '''
        eventInfo={'location':'M\\\"unster, Germany'}
        Event.fixEncodings(eventInfo,debug=True)
        self.assertEqual(eventInfo['location'],"Münster, Germany")
  
    def testCrossref(self):
        '''
        test loading crossref data
        '''
        crossRef=Crossref(debug=False,profile=True)
        if not crossRef.em.isCached():
            crossRef.cacheEvents()
        else:
            crossRef.em.fromStore()    
        self.assertTrue(crossRef.em.isCached())
        self.assertTrue(len(crossRef.em.events)>45000)

    def testCrossref_DOI_Lookup(self):
        ''' test crossref API access 
        see https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/28
        '''
        cr=Crossref()
        doimeta=cr.doiMetaData("10.1637/0005-2086-63.1.117")
        print (doimeta)
        self.assertTrue('title' in doimeta)
        title=doimeta['title'][0]
        print (title)
        self.assertEqual('Tenth International Symposium on Avian Influenza',title)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()