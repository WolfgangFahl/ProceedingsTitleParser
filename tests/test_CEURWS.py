'''
Created on 2020-07-06

@author: wf
'''
import unittest
from tests.basetest import Basetest
from ptp.ceurws import CeurWs, CeurWsEvent
from ptp.titleparser import TitleParser#

class TestCeurWs(Basetest):
    ''' test handling proceeding titles retrieved
    from http://ceur-ws.org/ Volumes '''

    def testCeurWsTitleParsing(self):
        ''' test CEUR-WS cache handling'''
        debug=self.debug
        cw=CeurWs(debug=debug)
        tp=TitleParser.getDefault()
        tc,errs,titles=cw.parseEvents(tp)
        if self.debug:
            print(len(titles))
        self.assertTrue(len(titles)>3000)
        em=cw.eventManager
        cw.addParsedTitlesToEventManager(titles, em)
        self.assertTrue(len(em.events)>940)
        em.store()
    
    def testExtract(self):
        ''' extract meta information from pages '''
        urls=['http://ceur-ws.org/Vol-2635/',
              'http://ceur-ws.org/Vol-2599/',
              'http://ceur-ws.org/Vol-2553/',
              'http://ceur-ws.org/Vol-2512/',
              'http://ceur-ws.org/Vol-2489/']
        expected=['DL4KG2020','BlockSW-CKG 2019','SemTab 2019','DI2KG2019','KGB-LASCAR 2019']
        events=[]
        for url in urls:
            event=CeurWsEvent()
            event.fromUrl(url)
            if self.debug:
                print (event)
            events.append(event)
        index=0    
        for event in events:
            self.assertEqual(expected[index],event.acronym)
            index+=1    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()