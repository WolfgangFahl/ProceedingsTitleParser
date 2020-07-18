'''
Created on 2020-07-12

@author: wf
'''
import unittest
from ptp.event import Event, EventManager


class TestEvent(unittest.TestCase):
    ''' test handling Events and EventManagers '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetLookupAcronym(self):
        ''' test fixing acronyms that contain no year '''
        eventinfos = [
            {"acronym":"FLAM 2013"},
            {"acronym": "IPTC", "year": 2014},
            {"acronym": "COMET", "year": "2012"},
            {"title":"Proceedings of the 50th North American Chemical Residue Workshop (NACRW)", "event": "NACRW", "year": 2013}
        ]
        fixed = ["FLAM 2013", "IPTC 2014", "COMET 2012", "NACRW 2013"]  
        for idx, eventinfo in enumerate(eventinfos):
            event = Event()
            event.fromDict(eventinfo)
            event.getLookupAcronym()
            self.assertEqual(fixed[idx], event.lookupAcronym)
            
    def testWikiSon(self):
        ''' test WikiSon format '''
        eventinfos = [
            { "acronym": "AAMAS 2015", 
              "city": "Istanbul", 
              "country": "Turkey", 
              "creation_date": "2016-09-29 18:38:27", 
              "event": "AAMAS 2015", "foundBy": "AAMAS 2015", "homepage": "http://www.aamas-conference.org/Proceedings/aamas2015/", "modification_date": "2016-09-29 18:38:27", "series": "AAMAS", "source": "OPEN RESEARCH", "start_date": "2015-01-01 00:00:00", "title": 'AAMAS 2015', "url": "https://www.openresearch.org/wiki/AAMAS 2015" }
        ]
        for eventinfo in eventinfos:
            eventDicts=[]
            event = Event()
            event.fromDict(eventinfo)
            event.getLookupAcronym()
            eventDicts.append(event.__dict__)
        wikison=EventManager.asWikiSon(eventDicts)    
        print (wikison)
        self.assertTrue('{{Event' in wikison)
        self.assertTrue('|event=AAMAS 2015' in wikison)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
