'''
Created on 2020-08-22

@author: wf
'''
import os
import yaml
from wikibot.mwTable import MediaWikiTable

class Query(object):
    ''' a Query e.g. for SPAQRL '''
    
    def __init__(self,name,query,lang='sparql',debug=False):
        '''
        constructor 
        Args:
            name(string): the name of the query
            query(string): the native Query text e.g. in SPARQL
            lang(string): the language of the query e.g. SPARQL
            debug(boolean): true if debug mode should be switched on
        '''
        self.name=name
        self.lang=lang
        self.query=query
        self.debug=debug
        
    def asWikiSourceMarkup(self):
        '''
        convert me to Mediawiki markup for syntax highlighting using the "source" tag
        
        Returns:
            string: the Markup
        '''
        markup="<source lang='%s'>\n%s\n</source>\n" %(self.lang,self.query)
        return markup
        
    def asWikiMarkup(self,sparql):
        '''
        run the given SPAQRL query, and convert result to MediaWiki markup
        
        Returns:
            string: the markup
        '''
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
        for name,queryText in QueryManager.getQueries().items():
            query=Query(name,queryText,debug=self.debug)
            self.queriesByName[name]=query
    
    @staticmethod
    def getQueries():
        path=os.path.dirname(__file__)
        queriesPath=path+"/../queries.yaml"
        with open(queriesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples
        