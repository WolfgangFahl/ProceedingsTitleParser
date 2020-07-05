'''
Created on 2020-06-21

@author: wf
'''
import unittest
import pyparsing as pp
from collections import Counter
from pyparsing import Word, alphas, nums, oneOf

class TestPyParsing(unittest.TestCase):
    ''' test core functionality of PyParsing library for usability in this project '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testParsing(self):
        ''' test py parsing library Word element '''
        greet = Word(alphas) + "," + Word(alphas) + "!"
        hello = "Hello, World!"
        parseString=greet.parseString(hello)
        self.assertEqual(4,len(parseString))
        print(hello, "->", parseString)
        
    def testProceedingsTitle(self):
        ''' test a simple py parsing grammar for proceedings titles '''
        pctitle_example="Proceedings of the 10th Symposium on Underwater and Hyperbaric Physiology. La Jolla, California, USA, July 1-2, 2002."
        pctitle=oneOf("Proceedings")+"of"+"the"+Word(nums)+oneOf("st nd th")+oneOf("Symposium Congress")+"on"
        print(pctitle.parseString(pctitle_example))
        
    @staticmethod    
    def doTestGrammars(examples,grammars):
        ''' test the given example strings against the given grammars '''
        # setup a counter
        matchCount=Counter()
        # loop over all potential strings
        for example in examples:
            matched=False
            # try out all grammars
            for grammarKey in grammars.keys():
                try:
                    grammar=grammars[grammarKey]
                    val=grammar.parseString(example)
                    matchCount[grammarKey]+=1
                    matched=True
                except pp.ParseException as pe:
                    pass
            # not grammar matching    
            if not matched:
                matchCount["failed"]+=1
                print (example)
        matches=matchCount.most_common(len(grammars)+2)  
        total=len(examples)
        print (matches) 
        for e in matches:
            grammarKey,found=e
            print ("%s: %4d (%3.1f %%)" % (grammarKey,found,found/total*100))            
            
    def testRegexpGrammars(self):
        examples=['10th ICACCT 2016']
        grammars={
            '4UpperCase+blank+4Year Digits'  : pp.Regex(r'^[A-Z]{4} \d{4}$'),
            '2-6 UpperCase+blank or dash+2-4 Digits': pp.Regex(r'[A-Z]{2-6}[ -]+\d{2-4}'),
            '10th 4-6 Uppercase 20##': pp.Regex(r'^10th\s[A-Z]{4,6}\s20[0-9][0-9]$') #   
            }
        
        TestPyParsing.doTestGrammars(examples, grammars)
        
            
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()