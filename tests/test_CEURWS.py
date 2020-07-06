'''
Created on 2020-07-06

@author: wf
'''
import unittest
from ptp.ceurws import CEURWS

class TestCEUWS(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testCEURWS(self):
        ''' test CEUR-WS '''
        cw=CEURWS()
        cw.cacheEvents()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()