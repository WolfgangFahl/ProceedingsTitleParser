'''
Created on 2020-04-09

@author: wf
'''
import re
class CorpusWordParser():
    def __init__(self):
        pass
    
    '''
    parse the given records
    '''
    def parse(self,records):
        print("parsing %d titles" % len(records))
        corpusWordusages=[]
        for record in records:
            wp=WordParser(record['source'],record['eventId'])
            wordusages=wp.parse(record['title'])
            corpusWordusages.extend(wordusages)
        print("found %d word usages" % len(corpusWordusages))  
        return corpusWordusages 
  
class WordUsage(object):
    '''
    a single word usage entry
    '''
    
    def __init__(self,index,word,source,eventId):
        self.pos=index+1
        self.word=word
        self.source=source
        self.eventId=eventId
         
class WordParser(object):
    '''
    Word based parser
    '''

    def __init__(self,source,eventId):
        '''
        Constructor
        Args:
            source(string): the source e.g. wikicfp
            eventId(string): the source specific id of the event
        '''
        self.source=source
        self.eventId=eventId
        
    def parse(self,title):
        '''
        parse the given title and return the word usages of it
        '''
        # split and return delimiters
        # https://stackoverflow.com/a/1059601/1497139
        words=re.split('(\W+)',title)
        wordusages=[]
        for index,word in enumerate(words):
            wordusage=WordUsage(index,word,self.source,self.eventId)
            wordusages.append(wordusage)
        return wordusages