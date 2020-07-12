'''
Created on 2020-07-12

@author: wf
'''
import unittest
from ptp.event import Event

class TestEvent(unittest.TestCase):
    ''' test handling Events and EventManagers '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testFixAcronym(self):
        ''' test fixing acronyms that contain no year '''
        eventinfos=[
            {"acronym":"FLAM 2013"}, 
            {"acronym": "IPTC","year": 2014}, 
            {"acronym": "COMET", "year": "2012"},
            {"title":"Proceedings of the 50th North American Chemical Residue Workshop (NACRW)", "event": "NACRW", "year": 2013}
        ]
        fixed=["FLAM 2013","IPTC 2014","COMET 2012","NACRW 2013"]  
        for idx,eventinfo in enumerate(eventinfos):
            event=Event()
            event.fromDict(eventinfo)
            event.fixAcronym()
            self.assertEqual(fixed[idx],event.acronym)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()