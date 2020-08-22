'''
Created on 2020-08-22

@author: wf
'''
import os
import yaml
from wikibot import mwTable
from wikibot.mwTable import MediaWikiTable

class Query(object):
    ''' a Query e.g. for SPAQRL '''
    
    def __init__(self,name,query,debug=False):
        '''constructor '''
        self.name=name
        self.query=query
        self.debug=debug
        
    def asWikiMarkup(self,sparql):
        listOfDicts=sparql.queryAsListOfDicts(self.query)
        if self.debug:
            print(listOfDicts)
        mwTable=MediaWikiTable()
        mwTable.fromListOfDicts(listOfDicts)
        markup=mwTable.asWikiMarkup()        
        return markup    

class QueryManager(object):
    '''
    manages prepackaged Queries
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.queriesByName={}
        self.debug=debug
        for name,sparql in QueryManager.getQueries().items():
            query=Query(name,sparql,debug=self.debug)
            self.queriesByName[name]=query
    
    @staticmethod
    def getQueries():
        path=os.path.dirname(__file__)
        queriesPath=path+"/../queries.yaml"
        with open(queriesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
        