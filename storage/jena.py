'''
Created on 2020-08-14

@author: wf
'''
from SPARQLWrapper import SPARQLWrapper, JSON

class Jena(object):
    '''
    wrapper for apache Jana
    '''


    def __init__(self,url,returnFormat=JSON):
        '''
        Constructor
        '''
        self.url=url
        self.sparql=SPARQLWrapper(url,returnFormat=returnFormat)
        
    def rawQuery(self,queryString):
        '''
        query with the given query string
        '''
        self.sparql.setQuery(queryString)
        queryResult = self.sparql.query()
        jsonResult=queryResult.convert()
        return jsonResult 
    
    def getResults(self,jsonResult):
        '''
        get the result from the given jsonResult
        '''
        return jsonResult["results"]["bindings"]

    def query(self,queryString):
        '''
        get a list of results for the given query
        '''
        jsonResult=self.rawQuery(queryString)
        return self.getResults(jsonResult)