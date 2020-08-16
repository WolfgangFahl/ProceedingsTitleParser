'''
Created on 2020-08-14

@author: wf
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.Wrapper import POSTDIRECTLY, POST
import datetime

class Jena(object):
    '''
    wrapper for apache Jana
    '''

    def __init__(self,url,mode='query',returnFormat=JSON, debug=False, typedLiterals=False):
        '''
        Constructor
        '''
        self.url="url%s" % (mode)
        self.mode=mode
        self.debug=debug
        self.typedLiterals=typedLiterals
        self.sparql=SPARQLWrapper(url,returnFormat=returnFormat)
        
    def rawQuery(self,queryString,method='POST'):
        '''
        query with the given query string
        '''
        self.sparql.setQuery(queryString)
        self.sparql.method=method
        queryResult = self.sparql.query()
        return queryResult 
    
    def getResults(self,jsonResult):
        '''
        get the result from the given jsonResult
        '''
        return jsonResult["results"]["bindings"]
    
    def insert(self,insertCommand):
        '''
        run an insert
        '''
        self.sparql.setRequestMethod(POSTDIRECTLY)
        response=self.rawQuery(insertCommand, method=POST)
        #see https://github.com/RDFLib/sparqlwrapper/issues/159#issuecomment-674523696
        # dummy read the body
        response.response.read()
        return response
    
    def getLocalName(self,name):
        '''
        retrieve valid localname from a string based primary key
        https://www.w3.org/TR/sparql11-query/#prefNames
        '''
        localName=''.join(ch for ch in name if ch.isalnum())
        return localName
    
    def insertListOfDicts(self,listOfDicts,entityType,primaryKey,prefixes):
        '''
        insert the given list of dicts mapping datatypes according to
        https://www.w3.org/TR/xmlschema-2/#built-in-datatypes
        
        mapped from 
        https://docs.python.org/3/library/stdtypes.html
        
        compare to
        https://www.w3.org/2001/sw/rdb2rdf/directGraph/
        http://www.bobdc.com/blog/json2rdf/
        https://www.w3.org/TR/json-ld11-api/#data-round-tripping
        https://stackoverflow.com/questions/29030231/json-to-rdf-xml-file-in-python
        '''
        errors=[]
        insertCommand='%s\nINSERT DATA {\n' % prefixes
        for index,record in enumerate(listOfDicts):
            if not primaryKey in record:
                errors.append["missing primary key %s in record %d",index]
            else:    
                primaryValue=record[primaryKey]
                encodedPrimaryValue=self.getLocalName(primaryValue)
                tSubject="<%s#%s>" %(entityType,encodedPrimaryValue)
                for keyValue in record.items():
                    key,value=keyValue
                    valueType=type(value)
                    if self.debug:
                        print("%s(%s)=%s" % (key,valueType,value))
                    tPredicate="%s_%s" % (entityType,key)
                    tObject=value    
                    if valueType == str:   
                        tObject='"%s"' % value
                    elif valueType==int:
                        if self.typedLiterals:
                            tObject='"%d"^^<http://www.w3.org/2001/XMLSchema#int>' %value
                        pass
                    elif valueType==float:
                        if self.typedLiterals:
                            tObject='"%s"^^<http://www.w3.org/2001/XMLSchema#double>' %value
                        pass
                    elif valueType==bool:
                        pass
                    elif valueType==datetime.date:
                        #if self.typedLiterals:
                        tObject='"%s"^^<http://www.w3.org/2001/XMLSchema#date>' %value
                        pass
                    else:
                        errors.append("can't handle type %s in record %d" % (valueType,index))
                        tObject=None
                    if tObject is not None:    
                        insertCommand+='  %s %s %s.\n' % (tSubject,tPredicate,tObject)
        insertCommand+="\n}"
        if self.debug:
            print (insertCommand)
        self.insert(insertCommand)
        return errors

    def query(self,queryString,method=POST):
        '''
        get a list of results for the given query
        '''
        queryResult=self.rawQuery(queryString,method=method) 
        jsonResult=queryResult.convert()
        return self.getResults(jsonResult)