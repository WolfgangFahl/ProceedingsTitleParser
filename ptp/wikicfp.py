'''
Created on 2020-08-20

@author: wf
'''
from ptp.event import EventManager
from ptp.webscrape import WebScrape
import datetime
import re

class WikiCFP(object):
    '''
    support events from http://www.wikicfp.com/cfp/
    '''

    def __init__(self, debug=False,profile=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.em=EventManager('wikicfp',url='http://www.wikicfp.com',title='WikiCFP',debug=debug,profile=profile)
      
class WikiCFPEvent(object):
    '''
    a single WikiCFPEvent
    '''
    def __init__(self,debug=False):
        self.debug=debug
            
    def fromTriples(self,rawEvent,triples): 
        '''
        get the rawEvent dict from the given triple e.g.:
        
        v:Event(v:summary)=IDC 2009
        v:Event(v:eventType)=Conference
        v:Event(v:startDate)=2009-06-03T00:00:00
        v:Event(v:endDate)=2009-06-05T23:59:59
        v:Event(v:locality)=Milano, Como, Italy
        v:Event(v:description)= IDC  2009 : The 8th International Conference on Interaction Design and Children
        v:Address(v:locality)=Milano, Como, Italy
        v:Event(v:summary)=Submission Deadline
        v:Event(v:startDate)=2009-01-19T00:00:00
        v:Event(v:summary)=Notification Due
        v:Event(v:startDate)=2009-02-20T00:00:00
        v:Event(v:summary)=Final Version Due
        v:Event(v:startDate)=2009-03-16T00:00:00
        '''
        recentSummary=None
        for s,p,o in triples:
            s=s.replace("v:","")
            p=p.replace("v:","")
            if self.debug:
                print ("%s(%s)=%s" % (s,p,o)) 
            if recentSummary in ['Submission Deadline','Notification Due','Final Version Due']:             
                key=recentSummary.replace(" ","_")
            else:
                key=p 
            if p.endswith('Date'):
                dateStr=o
                if dateStr=="TBD":
                    o=None
                else:    
                    o=datetime.datetime.strptime(
                        dateStr, "%Y-%m-%dT%H:%M:%S").date()
            if not key in rawEvent: 
                rawEvent[key]=o    
            if p=="summary": 
                recentSummary=o 
            else: 
                recentSummary=None
                           
    def fromEventId(self,eventId):
        '''
        see e.g. https://github.com/andreeaiana/graph_confrec/blob/master/src/data/WikiCFPCrawler.py
        '''
        url = "http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid="+str(eventId)
        return self.fromUrl(url)
    
    def fromUrl(self,url):
        '''
        get the event form the given url
        '''
        m=re.match("^.*//www.wikicfp.com/cfp/.*eventid=(\d+).*$",url)
        if not m:
            raise Exception("Invalid URL %s" % (url))
        else:
            eventId=int(m.group(1))
        scrape=WebScrape(debug=self.debug)
        triples=scrape.parseRDFa(url)
        rawEvent={}
        rawEvent['eventId']="wikiCFP#%d" % eventId
        rawEvent['wikiCFPId']=eventId
        self.fromTriples(rawEvent,triples)
        rawEvent['acronym']=rawEvent.pop('summary')
        rawEvent['title']=rawEvent.pop('description')
       
        return rawEvent
        