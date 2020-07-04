'''
Created on 04.07.2020

@author: wf
'''
from wikibot.smw import SMW
import os
from wikibot.wikibot import WikiBot
from titleparser.event import Event

class OpenResearch(object):
    '''
    OpenResearch Semantic Media API
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.smw=self.getSMW()
        
    def getEvent(self,pageTitle):
        ''' get the event with the given page title (if any) '''
        ask="""{{#ask: [["""+pageTitle+"""]]
|mainlabel=Event
| ?Acronym = acronym
| ?Event in series = series
| ?Homepage = homepage
| ?Has location city = city
| ?Has_location_country = country
| ?_CDAT = creation_date
| ?_MDAT = modification_date
}}
"""
        askResult=self.smw.query(ask)
        if len(askResult)==1:
            event=Event()
            event.fromAskResult(next(iter(askResult.values())))
        elif len(askResult)==0:
            event=None
        else:
            raise Exception("%s is ambigous %d result found" % (pageTitle,len(askResult)))        
        return event  

    def getSMW(self):
        wikibot=OpenResearch.getSMW_Wiki(self)
        smw=SMW(wikibot.site)
        return smw
        
    def getSMW_Wiki(self):
        wikiId="or"
        iniFile=WikiBot.iniFilePath(wikiId)
        if not os.path.isfile(iniFile):
            WikiBot.writeIni(wikiId,"OpenResearch.org","https://www.openresearch.org","/mediawiki/","MediaWiki 1.31.1")    
        wikibot=WikiBot.ofWikiId(wikiId)
        return  wikibot