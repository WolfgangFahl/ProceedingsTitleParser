'''
Created on 2020-07-11

@author: wf
'''
import unittest
from ptp.webserver import app
from ptp.titleparser import Title
#from json2xml import json2xml
from dicttoxml import dicttoxml
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
        query='/parse?titles=BIR+2019&metadebug=on'
        response=self.app.get(query)
        self.assertEqual(response.status_code, 200)
        if self.debug:
            print(response.data)
        self.assertIn(b'<!DOCTYPE html>',response.data)
        self.assertIn(b"Proceedings of the 8th International Workshop on Bibliometric-enhanced Information Retrieval (BIR 2019)",response.data)

    def testContentNegotiationJson(self):
        ''' test Content Negotiation '''
        query='/parse?titles=BIR+2019'
        response=self.app.get(query,headers={'accept':'application/json'})
        self.assertEqual(response.status_code, 200)
        eventResult=response.get_json()
        #if self.debug:
        print (eventResult)
        self.assertEqual(2,eventResult["count"])
        self.assertEqual(2,len(eventResult["events"]))
        
    #def testJson2XML(self):
    # https://github.com/vinitkumar/json2xml/issues/59
    #    ''' test Json  XML conversion '''
    #    jsonText='{"count": 1, "events": [{"acronym": "EuroPar 2020", "city": "Warsaw", "country": "Poland", "creation_date": "2020-02-27T14:44:52+00:00", "end_date": "2020-08-28T00:00:00+00:00", "event": "EuroPar 2020", "foundBy": "EuroPar 2020", "homepage": "https://2020.euro-par.org/", "modification_date": "2020-02-27T14:44:52+00:00", "series": "EuroPar", "source": "OPEN RESEARCH", "start_date": "2020-08-24T00:00:00+00:00", "title": "International European Conference on Parallel and Distributed Computing", "url": "https://www.openresearch.org/wiki/EuroPar 2020"}]}'
    #    xml=json2xml.Json2xml(jsonText).to_xml()  
    #    print(xml)   
    def testDict2XML(self):
        eventDict={"acronym": "EuroPar 2020", "city": "Warsaw", "country": "Poland", "creation_date": "2020-02-27T14:44:52+00:00", "end_date": "2020-08-28T00:00:00+00:00", "event": "EuroPar 2020", "foundBy": "EuroPar 2020", "homepage": "https://2020.euro-par.org/", "modification_date": "2020-02-27T14:44:52+00:00", "series": "EuroPar", "source": "OPEN RESEARCH", "start_date": "2020-08-24T00:00:00+00:00", "title": "International European Conference on Parallel and Distributed Computing", "url": "https://www.openresearch.org/wiki/EuroPar 2020"}
        xml=dicttoxml(eventDict)
        print(xml)
         
    def testContentNegotiationXml(self):
        ''' test content negotiation for XML '''
        query='/parse?titles=EuroPar+2020'   
        for accept in ['application/xml','text/xml']:
            response=self.app.get(query,headers={'accept': accept})
            self.assertEqual(response.status_code, 200)
            xml=response.get_data()
            print(xml)
            self.assertTrue("xml version" in xml.decode())
            
    def testFormatQueryParameterJson(self):
        query='/parse?titles=BIR+2019'
        response=self.app.get(query+"&format=json")
        self.assertEqual(response.status_code, 200)
        eventResult=response.get_json()
        #if self.debug:
        print (eventResult)
        self.assertEqual(4,eventResult["count"])
        self.assertEqual(4,len(eventResult["events"]))
        pass
    
    def testFormatQueryParameterXml(self):
        query='/parse?titles=EuroPar+2020'
        response=self.app.get(query+"&format=xml")
        self.assertEqual(response.status_code, 200)
        xml=response.get_data()
        print(xml)
        self.assertTrue("xml version" in xml.decode())
       
    def testFormatQueryParameterWikiSon(self):
        # test WikiSon handling
        query='/parse?titles=PAKM+2000'
        response=self.app.get(query+"&format=wikison")
        self.assertEqual(response.status_code, 200)
        wikison=response.get_data()
        print(wikison)
        self.assertTrue("{{Event" in wikison.decode())
        pass   
    
    def testFormatQueryParameterCsv(self):
        # test WikiSon handling
        query='/parse?titles=PAKM+2000'
        response=self.app.get(query+"&format=csv")
        self.assertEqual(response.status_code, 200)
        csv=response.get_data().decode()
        print(csv,flush=True)
        self.assertTrue('"acronym",' in csv)
        self.assertTrue('"Switzerland"'in csv)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
