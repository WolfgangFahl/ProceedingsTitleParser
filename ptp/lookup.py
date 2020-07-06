'''
Created on 06.07.2020

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
from ptp.openresearch import OpenResearch

class Lookup(object):
    '''
    Wrapper for TitleParser
    '''

    def __init__(self,name):
        '''
        Constructor
        '''
        self.ptp=ProceedingsTitleParser.getInstance()
        self.dictionary=ProceedingsTitleParser.getDictionary()
        # get the open research EventManager
        self.em=OpenResearch.getEventManager()
        self.tp=TitleParser(name=name,ptp=self.ptp,dictionary=self.dictionary,em=self.em) 
        