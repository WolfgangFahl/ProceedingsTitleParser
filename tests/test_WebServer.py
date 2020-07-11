'''
Created on 2020-07-11

@author: wf
'''
import unittest

from ptp.webserver import app

class TestWebServer(unittest.TestCase):
    ''' see https://www.patricksoftwareblog.com/unit-testing-a-flask-application/ '''

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        pass


    def tearDown(self):
        pass


    def testWebServer(self):
        query='/parse?titles=BIR+2019'
        response=self.app.get()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()