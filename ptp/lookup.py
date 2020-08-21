'''
Created on 06.07.2020

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
import ptp.openresearch
import ptp.ceurws
import ptp.confref
import ptp.wikidata
import ptp.dblp
import ptp.crossref
import ptp.wikicfp
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
        self.ems=[]
        if butNot is None:
            self.butNot=[]
        else:
            self.butNot=butNot
        lookupIds=['or']
        if getAll:
            lookupIds=['or','ceur-ws','crossref','confref','wikicfp','wikidata','dblp']
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
                elif lookupId=='crossref':
                    lem=ptp.crossref.Crossref(debug=self.debug)   
                elif lookupId=='wikicfp':
                    # http://www.wikicfp.com/cfp/
                    lem=ptp.wikicfp.WikiCFP(debug=self.debug)       
                elif lookupId=='wikidata':
                    # https://www.wikidata.org/wiki/Wikidata:Main_Page
                    lem=ptp.wikidata.WikiData(debug=self.debug)      
                elif lookupId=='dblp':
                    # https://dblp.org/
                    lem=ptp.dblp.Dblp(debug=self.debug)                
            if lem is not None:
                lem.initEventManager()
                self.ems.append(lem.em);
            
        self.tp=TitleParser(lookup=self,name=name,ptp=self.ptp,dictionary=self.dictionary,ems=self.ems)

    def extractFromUrl(self,url):
        ''' extract a record from the given Url '''
        result=None
        if '/ceur-ws.org/' in url:
            event=ptp.ceurws.CeurwsEvent()
            event.fromUrl(url)
            result={'source':'CEUR-WS','eventId': event.vol,'proceedingsUrl': event.proceedingsUrl,'title': event.title, 'acronym': event.acronym, 'loctime': event.loctime}
        elif '//doi.org/' in url:
            doi=url.replace("//doi.org/","")
            doi=doi.replace("https:","") 
            doi=doi.replace("http:","")
            return self.extractFromDOI(doi) 
        elif '//www.wikicfp.com/cfp' in url:
            wikiCFPEvent=ptp.wikicfp.WikiCFPEvent()
            rawEvent=wikiCFPEvent.fromUrl(url)
            result={'source':'wikicfp','eventId': rawEvent['eventId'], 'title': rawEvent['title'],'metadata':rawEvent}
            return result
        return result
    
    def extractFromDOI(self,doi):
        ''' extract Meta Data from the given DOI '''
        cr=ptp.crossref.Crossref()
        metadata=cr.doiMetaData(doi)
        title=metadata['title'][0]
        result={'source': 'Crossref','eventId': doi,'title':title, 'proceedingsUrl':'https://doi.org/%s' % doi,'metadata': metadata}
        return result

    @staticmethod
    def getExamples():
        path=os.path.dirname(__file__)
        examplesPath=path+"/../examples.yaml"
        with open(examplesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
