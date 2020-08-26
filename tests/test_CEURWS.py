'''
Created on 2020-07-06

@author: wf
'''
import unittest
import os
from ptp.ceurws import CEURWS, CeurwsEvent

class TestCEURWS(unittest.TestCase):
    ''' test handling proceeding titles retrieved
    from http://ceur-ws.org/ Volumes '''

    def setUp(self):
        self.debug=False
        self.forceCaching=False
        pass

    def tearDown(self):
        pass

    def testCEURWS(self):
        ''' test CEUR-WS cache handling'''
        cw=CEURWS(debug=self.debug)
        if self.forceCaching:
            cacheFile=cw.em.getCacheFile()
            if os.path.isfile(cacheFile):
                os.remove(cacheFile)
        if not cw.em.isCached():    
            cw.cacheEvents()
        else:
            cw.em.fromStore()    
        print(len(cw.em.events))
        self.assertTrue(cw.em.isCached())
        self.assertTrue(len(cw.em.events)>940)
        if cw.em.mode=='json':
            size=os.stat(cacheFile).st_size
            print (size)
            self.assertTrue(size>500000)
        pass
    
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
            event=CeurwsEvent()
            event.fromUrl(url)
            print (event)
            events.append(event)
        index=0    
        for event in events:
            self.assertEqual(expected[index],event.acronym)
            index+=1    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()