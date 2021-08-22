'''
Created on 2020-07-06

@author: wf
'''
from ptp.titleparser import ProceedingsTitleParser,TitleParser
import ptp.ceurws
import ptp.wikidataproceedings
import ptp.gnd
from lodstorage.sql import SQLDB
from lodstorage.entity import EntityManager
from lodstorage.storageconfig import StoreMode, StorageConfig
from datetime import datetime
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import copy
import os
import sys
import yaml

class Lookup(object):
    '''
    Wrapper for TitleParser
    '''

    def __init__(self,name,getAll=True,butNot=None,debug=False,singleDB=False):
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
        self.config=StorageConfig.getSQL()
        self.getLookupIds(butNot,getAll)        
        self.initEntityManagers(self.config,singleDB)
        self.tp=TitleParser(lookup=self,name=self.name,ptp=self.ptp,dictionary=self.dictionary,ems=self.ems)
        
    @staticmethod
    def ensureAllIsAvailable(msg=None):
        ''' 
        make sure the event_all database is available and return a suitable lookup
        '''    
        lookup=Lookup("CreateEventAll",singleDB=True,debug=True)
        if len(lookup.config.errors)>0:
            lookup.createEventAll(0, withWikiData=True)
            lookup=Lookup("CreateEventAll",singleDB=True,debug=True)
        else:
            if msg is not None:
                print("ensureAllIsAvailable no errors for %s" % msg)    
        return lookup    
        
    def setSingleDBConfig(self,config):    
        '''
        set the cacheFile to the singleDB "Event_all.db"
        Args:
            config(Storareconfig): the storage configuration to use
        ''' 
        # if event_all.db is available use it ...
        config.cacheFile=Lookup.getDBFile()
        # if cacheFile is not available
        if not os.path.isfile(config.cacheFile):
            config.errors=['cachefile %s is missing' % config.cacheFile]
            config.cacheFile=None
        else:
            config.errors=self.check(SQLDB(config.cacheFile),debug=self.debug)    
            # make sure the event_all db is complete
            if len(config.errors)>0:
                config.cacheFile=None
            else:
                config.singleDB=True
        
    def getLookupIds(self,butNot,getAll):    
        '''
        get the lookup ids
        Args:
            butNot(list): exclude the given list of ids
            getAll(boolean): true if all ids should be returned
        '''
        if butNot is None:
            self.butNot=[]
        else:
            self.butNot=butNot
        self.lookupIds=['or']
        if getAll:
            self.lookupIds=['or','ceur-ws','crossref','confref','dblp','gnd','wikicfp','wikidata']
        
    def initEntityManagers(self,config,singleDB):
        '''
        Args:
           config(StorageConfig): the configuration to use
           singleDB(boolean): True - if one database should be use for all entity managers
        '''        
        if singleDB:
            self.setSingleDBConfig(config)    
            if len(config.errors)>0:
                print("Warning: %s \nCan't use single database for all events" % config.errors)
        # get the open research EventManager
        self.ems=[]
        for lookupId  in self.lookupIds:
            lem=None
            if not lookupId in self.butNot:
                if lookupId=='or': 
                    # https://www.openresearch.org/wiki/Main_Page
                    lem=ptp.openresearch.OpenResearch(config=copy.copy(config))
                elif lookupId=='ceur-ws':
                    # CEUR-WS http://ceur-ws.org/
                    lem=ptp.ceurws.CEURWS(config=copy.copy(config))
                elif lookupId=='confref':
                    # confref http://portal.confref.org/
                    lem=ptp.confref.ConfRef(config=copy.copy(config))
                elif lookupId=='crossref':
                    # https://www.crossref.org/
                    lem=ptp.crossref.Crossref(config=copy.copy(config))   
                elif lookupId=='dblp':
                    # https://dblp.org/
                    lem=ptp.dblp.Dblp(config=copy.copy(config))  
                elif lookupId=='gnd': 
                    # https://d-nb.info/standards/elementset/gnd
                    lem=ptp.gnd.GND(config=copy.copy(config))
                elif lookupId=='wikicfp':
                    # http://www.wikicfp.com/cfp/
                    lem=ptp.wikicfp.WikiCFP(config=copy.copy(config))       
                elif lookupId=='wikidata':
                    # https://www.wikidata.org/wiki/Wikidata:Main_Page
                    lem=ptp.wikidataproceedings.WikiData(config=copy.copy(config))      
                              
            if lem is not None:
                lem.initEventManager()
                self.ems.append(lem.em);            

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
            wikiCFPEvent=ptp.wikicfp.WikiCFPEventFetcher()
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
        Args:
            debug(boolean): if True show debug information
        '''
        tableList=sqlDB.getTableList()
        if debug:
            print(tableList)
        # create hashmap of columns for tables
        tableCols={}
        for table in tableList:
            tableName=table['name']
            tableCols[tableName]=table['columns']
            
        tableSchemas=self.getEventSchemas()
        tableSchemas['City_github']='City List from github'
        tableSchemas['Country_github']='Country list from github'
        tableSchemas['Country_wikidata']='Country list from wikidata'
        tableSchemas['Province_wikidata']='Province list from wikidata'    
        tableSchemas['City_wikidata']='City list from wikidata'
        errors=[]
        for tableName in tableSchemas:
            if not tableName in tableCols:
                errors.append("table %s is missing" % tableName)
            elif self.debug:
                print("%s ✅" %tableName)
                for col in tableCols[tableName]:
                    print("  %2d: %s(%s)" % (col['cid'],col['name'],col['type']))
                    
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
            'Event_gnd': 'GND',
            'Event_wikicfp':'WikiCFP',
            'Event_wikidata':'PTP',
            'Event_dblp':'DBLP'}
        return eventSchemas
    
    @staticmethod
    def getDBFile(cacheFileName='Event_all'):
        '''
        get the database file for the given cacheFileName
        '''
        cachedir=StorageConfig.getDefault().getCachePath()
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
   select eventId,title,url,lookupAcronym,acronym,source,year from event_CEURWS
union 
   select eventId,title,url,lookupAcronym,acronym,source,year from event_crossref
union 
   select eventId,title,url,lookupAcronym,acronym,source,year from event_confref
union 
   select eventId,title,url,lookupAcronym,acronym,source,year from event_dblp   
union 
   select eventId,title,url,lookupAcronym,acronym,source,year from event_gnd     
union
   select eventId,title,url,lookupAcronym,acronym,source,year from event_or
union
   select eventId,title,url,lookupAcronym,acronym,source,year from event_wikicfp
union 
   select eventId,title,url,lookupAcronym,acronym,source,year from event_wikidata;
   '''
        sqlDB=self.getSQLDB()
        sqlDB.c.execute(viewDDL)
        
        
    def copyFrom(self,dbFile):
        '''
        copy the contents of the given database file to my database
        Args:
            dbFile(string): the database to copy the content from
        '''
        sqlDB=self.getSQLDB()
        sourceDB=SQLDB(dbFile)
        sourceDB.copyTo(sqlDB)
        
    def createEventAll(self,maxAgeMin=24*60,withWikiData=True,wikiDataEndpoint=ptp.wikidataproceedings.WikiData.defaultEndpoint):
        '''
        create the event all database
        
        Args:
            maxAgeH(int): maximum age of the database before being recreated
            withWikiData(boolean): True if the wikidata tables should be initialized
            wikiDataEndpoint(string): the url to the SPARQL endpoint to use for wikidata queries
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
                wikiEntityManagers=[CountryManager("wikidata"),ProvinceManager("wikidata"),CityManager("wikidata")]
                for wem in wikiEntityManagers:
                    wem.endpoint=wikiDataEndpoint
                    wem.fromCache()
                    self.copyFrom(wem.cacheFile)
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

__version__ = 0.1
__date__ = '2020-06-22'
__updated__ = '2020-08-20'    

DEBUG = 1

    
def main(argv=None): # IGNORE:C0111
    '''main program.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)    
        
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    user_name="Wolfgang Fahl"
    program_license = '''%s

  Created by %s on %s.
  Copyright 2020 Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, user_name,str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="show debug info")
        parser.add_argument('-e', '--endpoint', default=ptp.wikidataproceedings.WikiData.defaultEndpoint, help="SPARQL endpoint to use for wikidata queries")     
        parser.add_argument('-v', '--version', action='version', version=program_version_message)
        parser.add_argument('-a', '--all',action='store_true',default=False,help='create Event_all.db in cache')
        parser.add_argument('-c', '--check',action='store_true',default=False,help='check Event_all.db in cache')
        parser.add_argument('-w', '--wikidata',action='store_true',default=True,help='add wikidata entries')
        
        # Process arguments
        args = parser.parse_args()   
        lookup=Lookup("CreateEventAll",singleDB=args.check,debug=args.debug)
        if args.all:   
            lookup.createEventAll(0, withWikiData=args.wikidata,wikiDataEndpoint=args.endpoint)
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2         

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())