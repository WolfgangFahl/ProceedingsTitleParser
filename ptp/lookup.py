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
        self.tp=TitleParser(lookup=self,name=name,ptp=self.ptp,dictionary=self.dictionary,ems=ems) 
        
    def extractFromUrl(self,url):
        ''' extract a record from the given Url '''
        result=None
        if '/ceur-ws.org/' in url:
            event=ptp.ceurws.CeurwsEvent()
            event.fromUrl(url)
            result={'source':'CEUR-WS','eventId': event.vol,'title': event.title, 'acronym': event.acronym}
        return result