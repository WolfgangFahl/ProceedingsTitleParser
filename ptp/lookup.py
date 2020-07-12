'''
Created on 06.07.2020

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
import ptp.openresearch
import ptp.ceurws
import ptp.confref
import ptp.wikidata
import os
import yaml

class Lookup(object):
    '''
    Wrapper for TitleParser
    '''

    def __init__(self,name,getAll=True,butNot=None,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.ptp=ProceedingsTitleParser.getInstance()
        self.dictionary=ProceedingsTitleParser.getDictionary()
        # get the open research EventManager
        ems=[]
        if butNot is None:
            self.butNot=[]
        else:
            self.butNot=butNot
        lookupIds=['or']
        if getAll:
            lookupIds=['or','ceur-ws','confref','wikidata']
        for lookupId  in lookupIds:
            lem=None
            if not lookupId in self.butNot:
                if lookupId=='or': 
                    # https://www.openresearch.org/wiki/Main_Page
                    lem=ptp.openresearch.OpenResearch(debug=self.debug)
                elif lookupId=='ceur-ws':
                    # CEUR-WS http://ceur-ws.org/
                    lem=ptp.ceurws.CEURWS(debug=self.debug)
                elif lookupId=='confref':
                    # confref http://portal.confref.org/
                    lem=ptp.confref.ConfRef(debug=self.debug)
                elif lookupId=='wikidata':
                    # https://www.wikidata.org/wiki/Wikidata:Main_Page
                    lem=ptp.wikidata.WikiData(debug=self.debug)                  
            if lem is not None:
                lem.initEventManager()
                ems.append(lem.em);
            
        self.tp=TitleParser(lookup=self,name=name,ptp=self.ptp,dictionary=self.dictionary,ems=ems)

    def extractFromUrl(self,url):
        ''' extract a record from the given Url '''
        result=None
        if '/ceur-ws.org/' in url:
            event=ptp.ceurws.CeurwsEvent()
            event.fromUrl(url)
            result={'source':'CEUR-WS','eventId': event.vol,'title': event.title, 'acronym': event.acronym}
        return result

    @staticmethod
    def getExamples():
        path=os.path.dirname(__file__)
        examplesPath=path+"/../examples.yaml"
        with open(examplesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
