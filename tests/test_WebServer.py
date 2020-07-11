'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.webserver import app
from ptp.titleparser import Title

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

    def testJson(self):
        title=Title("");
        jsonText=title.asJson()
        #self.debug=True
        #if self.debug:
        print(jsonText)
        self.assertTrue('"count": 0' in jsonText)

    def testWebServer(self):
        ''' test the WebServer '''
        query='/parse?titles=BIR+2019'
        response=self.app.get(query)
        self.assertEqual(response.status_code, 200)
        if self.debug:
            print(response.data)
        self.assertIn(b'<!DOCTYPE html>',response.data)
        self.assertIn(b"Proceedings of the 8th International Workshop on Bibliometric-enhanced Information Retrieval (BIR 2019)",response.data)

    def testContentNegotiation(self):
        ''' test Content Negotiation '''
        query='/parse?titles=BIR+2019'
        response=self.app.get(query,headers={'accept':'application/json'})
        self.assertEqual(response.status_code, 200)
        eventResult=response.get_json()
        #if self.debug:
        print (eventResult)
        self.assertEqual(3,eventResult["count"])
        self.assertEqual(3,len(eventResult["events"]))

    def testFormatQueryParameter(self):
        query='/parse?titles=BIR+2019'
        response=self.app.get(query+"&format=json")
        self.assertEqual(response.status_code, 200)
        eventResult=response.get_json()
        #if self.debug:
        print (eventResult)
        self.assertEqual(3,eventResult["count"])
        self.assertEqual(3,len(eventResult["events"]))
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
