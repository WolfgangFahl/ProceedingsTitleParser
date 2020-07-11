'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.confref import ConfRef

class TestConfRef(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testConfRef(self):
        ''' test reading confRef data '''
        confRef=ConfRef()
        confRef.initEventManager()
        self.assertEqual(37945, len(confRef.rawevents))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()