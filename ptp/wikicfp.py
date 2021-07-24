"""
Created on 2020-08-20


  script to read event metadata from http://wikicfp.com
  
  use: python3 wikicfp.py [startId] [stopId] [threads]
  @param startId
  @param stopId
  @param threads - number of threads the script should create to improve performance
  
  example: python3 wikicfp.py --startId 2000 --stopId 2999 10

  @author:     svantje, wf
  @copyright:  2020 TIB Hannover, Wolfgang Fahl. All rights reserved.

"""
from ptp.event import EventManager, Event
from ptp.webscrape import WebScrape
import datetime
import glob
import re
import os
import sys
import threading
import time
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from lodstorage.storageconfig import StorageConfig

class WikiCFP(object):
    '''
    support events from http://www.wikicfp.com/cfp/
    '''

    def __init__(self,config=None,debug:bool=False,limit=200000,batchSize=1000):
        '''
        Constructor
        
        Args:
            config(StorageConfig): the storage configuration to use
            debug(bool): if True debug for crawling is on
            limit(int): maximum number of entries to be crawled
            batchSize(int): default size of batches
        '''
        self.debug=debug
        self.limit=limit
        self.batchSize=batchSize
        self.em=self.getEventManager(config)
        self.profile=self.em.config.profile
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        
    def getEventManager(self,config=None,mode='sql'):
        '''
        get an EventManager
        
        Args:
            config(StorageConfig): the storage configuration to use
            mode(string): the storage mode to use e.g. "json" - will select a config based on mode if config is None
        '''
        if config is None:
            if mode=='sql':
                config=StorageConfig.getSQL()
            elif mode=='json':
                config=StorageConfig.getJSON()
        em=EventManager('wikicfp',url='http://www.wikicfp.com',title='WikiCFP',config=config) 
        return em
    
    def cacheEvents(self):
        '''
        cache my events to my eventmanager
        '''
        jsonEm=self.getEventManager(mode='json')
        if jsonEm.isCached():
            jsonEm.fromStore()
        else:    
            self.crawlFilesToJson(jsonEm)
        for event in jsonEm.events.values():
            self.em.add(event)
        self.em.store(limit=self.limit, batchSize=self.batchSize)    
        
    def crawlFilesToJson(self,jsonEm):    
        '''
        convert the crawlFiles to Json
        
        Args:
            jsonEm(EventManager): the JSON - storage based Eventmanager to use to collect the results
        '''
        # crawling is not done on startup but need to be done
        # in command line mode ... we just collect the json crawl result files here
        #self.crawl(startId=startId,stopId=stopId)
        startTime=time.time()
        for jsonFilePath in self.jsonFiles():
            batchEm=self.getEventManager(mode='json')
            batchEm.fromStore(cacheFile=jsonFilePath)
            if self.debug:
                print("%4d: %s" % (len(batchEm.events),jsonFilePath))
            for event in batchEm.events.values():
                if hasattr(event,'title') and event.title is not None:
                    event.source=self.em.name
                    for field in ['startDate','endDate','locality','Submission_Deadline','Notification_Due','year']:
                        if not hasattr(event,field):
                            event.__dict__[field]=None
                    if event.startDate is not None:
                        event.year=event.startDate.year
                    event.url=WikiCFPEvent.getEventUrl(event.wikiCFPId)
                    jsonEm.add(event)
        if self.profile:
            print ("read %d events in %5.1f s" % (len(self.em.events),time.time()-startTime))
        jsonEm.store(limit=self.limit,batchSize=self.batchSize)
     
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms() 
        
    def jsonFiles(self):  
        '''
        get the list of the json files that have my data
        '''
        jsonFiles=sorted(glob.glob(self.jsondir+"wikicfp_*.json"),key=lambda path:int(re.findall(r'\d+',path)[0]))
        return jsonFiles    
        
    def getJsonFileName(self,startId,stopId):
        '''
        get the JsonFileName for the given startId to stopId
        '''
        jsonFilePath=self.jsondir+"wikicfp_%06d-%06d.json" % (startId,stopId)
        return jsonFilePath
        
    def crawl(self,threadIndex,startId,stopId):
        '''
        see https://github.com/TIBHannover/confIDent-dataScraping/blob/master/wikicfp.py
        '''
        if startId <= stopId: step = +1
        else: step = -1
        print('crawling (%2d) WikiCFP from %d to %d' % (threadIndex,startId,stopId))
        jsonFilepath=self.getJsonFileName(startId,stopId)
        batchEm=self.getEventManager(mode='json')
 
        # get all ids
        for eventId in range(int(startId), int(stopId+1), step):
            wEvent=WikiCFPEvent()
            rawEvent=wEvent.fromEventId(eventId)
            event=Event()
            event.fromDict(rawEvent)
            batchEm.add(event)
            title="? deleted: %r" %event.deleted if not 'title' in rawEvent else event.title
            print("%06d: %s" % (eventId,title))
        batchEm.store(cacheFile=jsonFilepath)
        return jsonFilepath
            
    def threadedCrawl(self,threads,startId,stopId):
        '''
        crawl with the given number of threads, startId and stopId
        
        Args:
           threads(int): number of threads to use
           startId(int): id of the event to start crawling with
           stopId(int): id of the event to stop crawling
        '''
        # determine the eventId range for each threaded job
        total = stopId-startId+1
        batchSize = total / threads
        startTime=time.time()
        
        msg='Crawling WikiCFP from %d - %d with %d threads with batches of %d event IDs each' % (startId,stopId,threads,batchSize)
        print(msg)

        # this list will contain all threads -> we can wait for all to finish at the end
        jobs = []

        # now start each thread with its id range and own filename
        for threadIndex in range(threads):

            s = startId + threadIndex * batchSize
            e = s + batchSize-1
        
            thread = threading.Thread(target = self.crawl, args=(threadIndex,s, e))
            jobs.append(thread)
            
        for job in jobs:
            job.start()   

        # wait till all threads have finished before print the last output
        for job in jobs:
            job.join()

        if self.debug:
            print('crawling done after %5.1f s' % (time.time()-startTime))
               
      
class WikiCFPEvent(object):
    '''
    a single WikiCFPEvent
    '''
    def __init__(self,debug=False,showProgress:bool=True):
        '''
        construct me
        
        Args:
            showProgress(bool): if True show progress
        
        '''
        self.debug=debug
        self.showProgress=showProgress
        self.progressCount=0
            
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
                
    @staticmethod       
    def getEventUrl(eventId):
        url= "http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid="+str(eventId)
        return url   
    
    @classmethod
    def getLatestEvent(cls,debug=False,showProgress=True):
        '''
        get the latest Event doing a binary search
        '''
        wikicfp=WikiCFPEvent(debug,showProgress=showProgress)
        wikicfp.progressCount=0
        wikicfp.getLatestEventFromPair()
        
    def getHighestNonDeletedIdInRange(self,fromId:int,toId:int)->int:
        '''
        get the event with the highest id int the range fromId to toId that is not deleted
        
        Args:
            fromId(int): minimum id to search from
            toId(int): maximum id to search to
            
        Returns:
            int: maxium id of an event that is not deleted or None if there is none in this range
        '''
        maxId=None
        for eventId in range(fromId,toId+1):
            if self.showProgress:
                print(".",end='',flush=True)
                self.progressCount+=1
                if self.progressCount % 50 == 0:
                    print(flush=True)
            rawEvent=self.fromEventId(eventId)
            if not rawEvent['deleted']:
                maxId=eventId
        return maxId
    
    def getLatestEventFromPair(self,low=5000,high=300000,margin=40):
        '''
        get the latest Event doing a binary search
        
        Args:
            low(int): lower index to search from
            hight(int): upper index boundary
        '''
        if high-low>margin+1:
            mid=(high+low)//2
            midId=(self.getHighestNonDeletedIdInRange(mid-margin, mid))
            if midId:
                return self.getLatestEventFromPair(mid+1,high)
            else:
                return self.getLatestEventFromPair(low, mid-1)
        else:
            return mid
        pass
                           
    def fromEventId(self,eventId):
        '''
        see e.g. https://github.com/andreeaiana/graph_confrec/blob/master/src/data/WikiCFPCrawler.py
        '''
        url=WikiCFPEvent.getEventUrl(eventId)
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
        rawEvent={}
        rawEvent['eventId']="wikiCFP#%d" % eventId
        rawEvent['wikiCFPId']=eventId
        rawEvent['deleted']=False
    
        scrape=WebScrape(debug=self.debug)
        triples=scrape.parseRDFa(url)
        if len(triples)==0:
            #scrape.printPrettyHtml(scrape.soup)
            firstH3=scrape.fromTag(scrape.soup, 'h3')
            if "This item has been deleted" in firstH3:
                rawEvent['deleted']=True
        else:        
            self.fromTriples(rawEvent,triples)
            # add series information
            seriesRegexp=r'/cfp/program\?id=([0-9]+).*'
            seriesLink=scrape.soup.find('a',href=re.compile(seriesRegexp))
            if seriesLink:
                # Tag: <a href="/cfp/program?id=1769&amp;s=ISWC&amp;f=International Semantic Web Conference">International Semantic Web Conference</a>
                href=seriesLink['href']
                m=re.match(seriesRegexp,href)
                if m:
                    rawEvent['seriesId']=m.group(1)
                    rawEvent['series']=seriesLink.text
                pass
                
            if 'summary' in rawEvent:
                rawEvent['acronym']=rawEvent.pop('summary').strip()
            if 'description' in rawEvent:
                rawEvent['title']=rawEvent.pop('description').strip()
           
        return rawEvent
    
__version__ = 0.2
__date__ = '2020-06-22'
__updated__ = '2021-07-24'    

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
  Copyright 2020-2021 TIB Hannover, Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,user_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="count", help="set debug level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('--startId', type=int, help='eventId to start crawling from', required=True)
        parser.add_argument('--stopId', type=int, help='eventId to stop crawling at', required=True)
        parser.add_argument('-t','--threads', type=int, help='number of threads to start', default=10)

        # Process arguments
        args = parser.parse_args()
        wikiCFP=WikiCFP(debug=args.debug)
        wikiCFP.threadedCrawl(args.threads, args.startId, args.stopId)
        
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
