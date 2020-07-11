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
        self.app = app.test_client()
        self.debug=False
        pass

    def tearDown(self):
        pass

    def testWebServer(self):
        query='/parse?titles=BIR+2019'
        response=self.app.get(query)
        self.assertEqual(response.status_code, 200)
        if self.debug:
            print(response.data)
        self.assertIn(b'<!DOCTYPE html>',response.data)
        self.assertIn(b"Proceedings of the 8th International Workshop on Bibliometric-enhanced Information Retrieval (BIR 2019)",response.data)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()