'''
Created on 2021-08-24

@author: wf
'''
from unittest import TestCase
import os
import time
import getpass
from corpus.eventcorpus import EventCorpus
from corpus.event import EventStorage
from corpus.lookup import CorpusLookup

class Basetest(TestCase):
    '''
    base test case
    '''
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EventStorage.profile=False
        profiler=Profiler("getting Corpus Lookup")
        EventCorpus.download()
        cls.corpusLookup=CorpusLookup(lookupIds=[])
        cls.corpusLookup.load()
        profiler.time()
    
    def setUp(self,debug=False,profile=True):
        '''
        setUp test environment
        '''
        TestCase.setUp(self)
        self.debug=debug
        self.profile=profile
        msg=f"test {self._testMethodName}, debug={self.debug}"
        self.profiler=Profiler(msg,profile=self.profile)
        self.lookup=self.__class__.corpusLookup
        
        
    def tearDown(self):
        TestCase.tearDown(self)
        self.profiler.time()    
        
    def inCI(self):
        '''
        are we running in a Continuous Integration Environment?
        '''
        publicCI=getpass.getuser() in ["travis", "runner"] 
        jenkins= "JENKINS_HOME" in os.environ;
        return publicCI or jenkins

class Profiler:
    '''
    simple profiler
    '''
    def __init__(self,msg,profile=True):
        '''
        construct me with the given msg and profile active flag
        
        Args:
            msg(str): the message to show if profiling is active
            profile(bool): True if messages should be shown
        '''
        self.msg=msg
        self.profile=profile
        self.starttime=time.time()
        if profile:
            print(f"Starting {msg} ...")
    
    def time(self,extraMsg=""):
        '''
        time the action and print if profile is active
        '''
        elapsed=time.time()-self.starttime
        if self.profile:
            print(f"{self.msg}{extraMsg} took {elapsed:5.1f} s")
        return elapsed