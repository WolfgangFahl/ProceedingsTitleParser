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
from storage.sql import SQLDB
from storage.entity import EntityManager
from storage.config import StoreMode
import io
import os
import sqlite3
import time
import yaml

class Lookup(object):
    '''
    Wrapper for TitleParser
    '''

    def __init__(self,name,getAll=True,butNot=None,debug=False):
        '''
        Constructor
        
        Args:
            name(string): the name of this lookup
            getAll(boolean): True if all sources should be considered
            butNot(list): a list of sources to be ignored
            debug(boolean): if True debug information should be shown
        '''
        self.name=name
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
        ''' 
        extract a record from the given Url (scrape mode)
        
        Args:
            url(string): the url to extract from
        '''
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
        ''' extract Meta Data from the given DOI 
        Args:
           doi(string): the DOI to extract the meta data for
        '''
        cr=ptp.crossref.Crossref()
        metadata=cr.doiMetaData(doi)
        title=metadata['title'][0]
        result={'source': 'Crossref','eventId': doi,'title':title, 'proceedingsUrl':'https://doi.org/%s' % doi,'metadata': metadata}
        return result
    
    def store(self,cacheFileName):
        '''
        store my contents to the given cacheFileName - 
        implemented as SQL storage
        '''
        cachedir=EntityManager.getCachePath()
        dbfile="%s/%s.db" % (cachedir,cacheFileName) 
        dbfile=os.path.abspath(dbfile)
        # remove existing database dump if it exists
        if os.path.exists(dbfile):
            os.remove(dbfile)
        backup=SQLDB(dbfile)    
        errors=[]
        print ("storing %s to %s" % (self.name,dbfile))  
        # debugging of CREATE TABLE 
        # backup.c.execute("CREATE TABLE Event_test(foundBy TEXT)")
        for em in self.ems:
            if not em.config.mode is StoreMode.SQL:
                raise Exception("lookup store only support SQL storemode but found %s for %s" % (em.config.mode,em.name))
            else:
                cacheFile=em.getCacheFile()
                sqlDB=em.getSQLDB(cacheFile)
                startTime=time.time()
                dump="\n".join(sqlDB.c.iterdump())
                #cursor.executescript(dump)
                print("finished getting dump of %s in %5.1f s" % (em.name,time.time()-startTime))
                dumpErrors=self.executeDump(backup.c,dump,em.name)
                errors.extend(dumpErrors)
                #sqlDB.backup(dbfile)
        backup.close()
        return errors
        
    def executeDump(self,connection,dump,title,maxErrors=100,errorDisplayLimit=12):
        '''
        execute the given dump for the given connection
        
        Args:
            connection(Connection): the sqlite3 connection to use
            dump(string): the SQL commands for the dump
            title(string): the title of the dump
            maxErrors(int): maximum number of errors to be tolerated before stopping and doing a rollback
        '''
        if self.debug:
            self.showDump(dump)
        startTime=time.time()    
        print("dump of %s has size %4.1f MB" % (title,len(dump)/1024/1024))
        errors=[]
        index=0
        # fixes https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/37
        for line in dump.split(";\n"):
            try:
                connection.execute(line)
            except  sqlite3.OperationalError as soe:
                msg="SQL error %s in line %d:\n\t%s" % (soe,index,line)
                errors.append(msg)
                if len(errors)<=errorDisplayLimit:
                    print(msg)    
                if len(errors)>=maxErrors:
                    connection.execute("ROLLBACK;")
                    break
                
            index=index+1
        print("finished excuting dump %s with %d lines and %d errors in %5.1f s" % (title,index,len(errors),time.time()-startTime))    
        return errors
        
    def showDump(self,dump,limit=10):
        '''
        show the given dump up to the given limit
        
        Args:
            dump(string): the SQL dump to show
            limit(int): the maximum number of lines to display
        '''
        s=io.StringIO(dump)
        index=0
        for line in s:
            if index <= limit:
                print(line)
                index+=1    
            else:
                break    

    @staticmethod
    def getExamples():
        path=os.path.dirname(__file__)
        examplesPath=path+"/../examples.yaml"
        with open(examplesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
