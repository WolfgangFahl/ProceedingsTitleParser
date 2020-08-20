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
import re
import os
import sys
import threading
import time
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class WikiCFP(object):
    '''
    support events from http://www.wikicfp.com/cfp/
    '''

    def __init__(self,debug=False,profile=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.profile=profile
        self.em=self.getEventManager(debug, profile)
        
    def getEventManager(self,debug=False,profile=False,mode='sparql'):
        '''
        get an EventManager
        '''
        em=EventManager('wikicfp',url='http://www.wikicfp.com',title='WikiCFP',debug=debug,profile=profile,mode=mode)
        return em
    
    def cacheEvents(self,startId=3860,stopId=3870):
        '''
        cache my events to my eventmanager
        '''
        jsonEm=self.getEventManager(self.debug,self.profile, 'json')
        if jsonEm.isCached():
            jsonEm.fromStore()
        else:
            #self.crawl(startId=startId,stopId=stopId)
            pass
     
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractCheckedAcronyms() 
        
    def getJsonFileName(self,startId,stopId):
        '''
        get the JsonFileName for the given startId to stopId
        '''
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        jsonFilePath=self.jsondir+"wikicfp_%04d-%04d.json" % (startId,stopId)
        return jsonFilePath
        
    def crawl(self,threadIndex,startId,stopId):
        '''
        see https://github.com/TIBHannover/confIDent-dataScraping/blob/master/wikicfp.py
        '''
        if startId <= stopId: step = +1
        else: step = -1
        print('crawling (%2d) WikiCFP from %d to %d' % (threadIndex,startId,stopId))
        jsonFilepath=self.getJsonFileName(startId,stopId)
        batchEm=self.getEventManager(self.debug,self.profile, 'json')
 
        # get all ids
        for eventId in range(int(startId), int(stopId), step):
            wEvent=WikiCFPEvent()
            rawEvent=wEvent.fromEventId(eventId)
            event=Event()
            event.fromDict(rawEvent)
            batchEm.add(event)
            if eventId%100==0:
                print("\n%05d" % eventId,end='',flush=True)
            print(".",end='',flush=True)
        batchEm.store(cacheFile=jsonFilepath)
            
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
        if 'summary' in rawEvent:
            rawEvent['acronym']=rawEvent.pop('summary')
        if 'description' in rawEvent:
            rawEvent['title']=rawEvent.pop('description')
       
        return rawEvent
    
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
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2020 TIB Hannover, Wolfgang Fahl. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

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
