'''
Created on 2020-07-25

@author: wf
'''
import unittest
from ptp.crossref import Crossref


class TestCrossref(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCrossref(self):
        ''' test crossref API access 
        see https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/28
        '''
        cr=Crossref()
        doimeta=cr.doiMetaData("10.1637/0005-2086-63.1.117")
        print (doimeta)
        self.assertTrue('title' in doimeta)
        title=doimeta['title'][0]
        print (title)
        self.assertEqual('Tenth International Symposium on Avian Influenza',title)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()