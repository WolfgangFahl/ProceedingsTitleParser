'''
Created on 2020-08-30

@author: wf
'''
import unittest
from ptp.lookup import Lookup

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
        test the number of sources
        '''
        lookup=Lookup("test")
        self.assertEqual(7,len(lookup.ems))
        lookup.store('Event_all')
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()