'''
Created on 2020-07-10

@author: wf
'''
import unittest
from ptp.lookup import Lookup

class TestExamples(unittest.TestCase):
    '''
    test the example yaml file handling
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testExamples(self):
        examples=Lookup.getExamples()
        print (examples)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()