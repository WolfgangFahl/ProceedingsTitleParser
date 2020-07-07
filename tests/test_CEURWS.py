'''
Created on 2020-07-06

@author: wf
'''
import unittest
from ptp.ceurws import CEURWS

class TestCEUWS(unittest.TestCase):
    ''' test handling proceeding titles retrieved
    from http://ceur-ws.org/ Volumes '''


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testCEURWS(self):
        ''' test CEUR-WS '''
        cw=CEURWS(debug=True)
        cw.cacheEvents()
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()