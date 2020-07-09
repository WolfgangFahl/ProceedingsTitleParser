'''
Created on 06.07.2020

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
import ptp.openresearch 
import ptp.ceurws 

class Lookup(object):
    '''
    Wrapper for TitleParser
    '''

    def __init__(self,name,getAll=True):
        '''
        Constructor
        '''
        self.ptp=ProceedingsTitleParser.getInstance()
        self.dictionary=ProceedingsTitleParser.getDictionary()
        # get the open research EventManager
        self.opr=ptp.openresearch.OpenResearch()
        self.opr.initEventManager()
        ems=[self.opr.em]
        if getAll:
            self.ceurws=ptp.ceurws.CEURWS(debug=True)
            self.ceurws.initEventManager()
            ems.append(self.ceurws.em)
        self.tp=TitleParser(name=name,ptp=self.ptp,dictionary=self.dictionary,ems=ems) 
        