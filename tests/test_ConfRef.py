'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.confref import ConfRef
#from storage.dgraph import Dgraph
#import getpass

class TestConfRef(unittest.TestCase):
    ''' test handling for data from portal.confref.org '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass

    def testConfRef(self):
        ''' test reading confRef data '''
        #host='localhost'
        #if getpass.getuser()=="wf":
        #    host='venus'
        #dgraph=Dgraph(host=host)
        # switch off due to https://discuss.dgraph.io/t/dgraph-v20-07-0-v20-03-0-unreliability-in-mac-os-environment/9376
        # dgraph.drop_all()
#        schema='''
#         identifier: string @index(exact) .
#         acronym: string .
#         country: string .
#         city: string .
#type Event {
#   identifier
#   acronym
#   country
#   city
#}
#        '''
        #dgraph.addSchema(schema)
        #mode="dgraph"
        mode='sparql'
        endpoint="http://localhost:3030/cr"
        limit=100000
        batchSize=2000
        confRef=ConfRef(mode=mode,endpoint=endpoint,debug=False,profile=True)
        confRef.em.removeCacheFile()
        #EventManager.debug=True
        confRef.cacheEvents(limit=limit,batchSize=batchSize)
        foundEvents=len(confRef.rawevents)
        cachedEvents=len(confRef.em.events)
        confRef.em.extractCheckedAcronyms() 
        self.assertEqual(37945,foundEvents)
        self.assertEqual(37945,cachedEvents)
        print("found %d  and cached %d events from confref" % (foundEvents,cachedEvents))
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
