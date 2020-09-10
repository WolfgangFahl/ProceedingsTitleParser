'''
Created on 06.07.2020

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
from ptp.location import CityManager, ProvinceManager, CountryManager
import ptp.openresearch
import ptp.ceurws
import ptp.confref
import ptp.wikidata
import ptp.dblp
import ptp.crossref
import ptp.wikicfp
from lodstorage.sql import SQLDB
from storage.entity import EntityManager
from storage.config import StoreMode, StorageConfig
from datetime import datetime
import os
import yaml
import getpass

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
        config=StorageConfig.getSQL()
        # if event_all.db is available use it ...
        config.cacheFile=Lookup.getDBFile()
        if not os.path.isfile(config.cacheFile):
            config.cacheFile=None
        else:
            self.check(SQLDB(config.cacheFile))    
        # get the open research EventManager
        self.ems=[]
        if butNot is None:
            self.butNot=[]
        else:
            self.butNot=butNot
        lookupIds=['or']
        if getAll:
            if config.cacheFile is None:
                maxAgeMin=1
                withWikiData=getpass.getuser()!="travis"
                self.createEventAll(maxAgeMin, withWikiData)
            lookupIds=['or','ceur-ws','crossref','confref','wikicfp','wikidata','dblp']
        for lookupId  in lookupIds:
            lem=None
            if not lookupId in self.butNot:
                if lookupId=='or': 
                    # https://www.openresearch.org/wiki/Main_Page
                    lem=ptp.openresearch.OpenResearch(config=config)
                elif lookupId=='ceur-ws':
                    # CEUR-WS http://ceur-ws.org/
                    lem=ptp.ceurws.CEURWS(config=config)
                elif lookupId=='confref':
                    # confref http://portal.confref.org/
                    lem=ptp.confref.ConfRef(config=config)
                elif lookupId=='crossref':
                    # https://www.crossref.org/
                    lem=ptp.crossref.Crossref(config=config)   
                elif lookupId=='dblp':
                    # https://dblp.org/
                    lem=ptp.dblp.Dblp(config=config)  
                elif lookupId=='wikicfp':
                    # http://www.wikicfp.com/cfp/
                    lem=ptp.wikicfp.WikiCFP(config=config)       
                elif lookupId=='wikidata':
                    # https://www.wikidata.org/wiki/Wikidata:Main_Page
                    lem=ptp.wikidata.WikiData(config=config)      
                              
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
    
    def check(self,sqlDB,debug=False):
        '''
        check the sqlDB to be o.k.
        '''
        tableList=sqlDB.getTableList()
        if debug:
            print(tableList)
        # create hashmap for tables
        tableDict={}
        for table in tableList:
            tableName=table['name']
            tableDict[tableName]=True
            
        tableSchemas=self.getEventSchemas()
        tableSchemas['City_github']='City List from github'
        tableSchemas['Country_github']='Country list from github'
        errors=[]
        for tableName in tableSchemas:
            if not tableName in tableDict:
                errors.append("table %s is missing" % tableName)
        return errors
    
    def getEventSchemas(self):
        '''
        get the table schemas
        '''
        eventSchemas={
            'Event_or': 'Open Research Entities',
            'Event_CEURWS':'PTP',
            'Event_crossref':'Crossref',
            'Event_confref':'Confref',
            'Event_wikicfp':'WikiCFP',
            'Event_wikidata':'PTP',
            'Event_dblp':'DBLP'}
        return eventSchemas
    
    @staticmethod
    def getDBFile(cacheFileName='Event_all'):
        '''
        get the database file for the given cacheFileName
        '''
        cachedir=EntityManager.getCachePath()
        dbfile="%s/%s.db" % (cachedir,cacheFileName) 
        dbfile=os.path.abspath(dbfile)
        return dbfile
    
    def getSQLDB(self,cacheFileName='Event_all'):
        '''
        get the SQLDB
        
        Args:
            cacheFileName(string): prefix of database file name
            
        Returns:
            SQLDB: the SQLDB access
        '''
        dbfile=Lookup.getDBFile(cacheFileName)
        sqlDB=SQLDB(dbfile)   
        return sqlDB
    
    def createView(self):
        ''' 
          create the general Event view
          
        Args:
            cacheFileName(string): the path to the database
        '''
        viewDDL='''create view event as 
   select eventId,title,url,lookupAcronym,acronym,source from event_CEURWS
union 
   select eventId,title,url,lookupAcronym,acronym,source from event_crossref
union 
   select eventId,title,url,lookupAcronym,acronym,source from event_confref
union 
   select eventId,title,url,lookupAcronym,acronym,source from event_dblp   
union
   select eventId,title,url,lookupAcronym,acronym,source from event_or
union
   select eventId,title,url,lookupAcronym,acronym,source from event_wikicfp
union 
   select eventId,title,url,lookupAcronym,acronym,source from event_wikidata;
   '''
        sqlDB=self.getSQLDB()
        sqlDB.c.execute(viewDDL)
        
        
    def copyFrom(self,dbFile):
        '''
        copy the contents of the given database file to my database
        '''
        sqlDB=self.getSQLDB()
        sourceDB=SQLDB(dbFile)
        sourceDB.copyTo(sqlDB)
        
    def createEventAll(self,maxAgeMin=24*60,withWikiData=True):
        '''
        create the event all database
        
        Args:
            maxAgeH(int): maximum age of the database before being recreated
            
        '''
        dbFile=Lookup.getDBFile()
        doCreate=True
        if os.path.isfile(dbFile):     
            st=os.stat(dbFile)
            ctime=datetime.fromtimestamp(st.st_ctime)
            now=datetime.now()
            age=now-ctime;
            ageMin=age.total_seconds()/60
            doCreate=ageMin>=maxAgeMin
            
        if doCreate:
            self.store()
            self.createView()
            
            cim=CityManager(name="github")
            cim.fromLutangar()
            dbFile=cim.store(cim.cityList)
            self.copyFrom(dbFile)
            
            cm=CountryManager("github",debug=True)
            cm.fromErdem()        
            dbFile=cm.store(cm.countryList)
            self.copyFrom(dbFile)
            
            wordUsageDBFile=Lookup.getDBFile("wordusage")
            if os.path.isfile(wordUsageDBFile):
                self.copyFrom(wordUsageDBFile)
            
            if withWikiData:
                cm=CountryManager("wikidata")
                cm.endpoint="https://query.wikidata.org/sparql"
                dbFile=cm.fromCache()       
                self.copyFrom(dbFile)
                
                pm=ProvinceManager("wikidata")
                pm.endpoint=cm.endpoint
                dbFile=pm.fromCache()
                self.copyFrom(dbFile)
        return self.getSQLDB()
    
    def store(self,cacheFileName='Event_all'):
        '''
        store my contents to the given cacheFileName - 
        implemented as SQL storage
        
        Args:
            cacheFileName(string): the path to the database
        '''
        dbfile=Lookup.getDBFile(cacheFileName)
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
                cacheFile=em.getCacheFile(config=em.config,mode=StoreMode.SQL)
                sqlDB=em.getSQLDB(cacheFile)
                sqlDB.copyTo(backup)
        backup.close()
        return errors

    @staticmethod
    def getExamples():
        path=os.path.dirname(__file__)
        examplesPath=path+"/../examples.yaml"
        with open(examplesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
