'''
Created on 2020-08-14

@author: wf
'''
from SPARQLWrapper import SPARQLWrapper2
from SPARQLWrapper.Wrapper import POSTDIRECTLY, POST
import datetime
import time

class SPARQL(object):
    '''
    wrapper for SPARQL e.g. Apache Jena, Virtuoso, Blazegraph
    
    :ivar url: full endpoint url (including mode)
    :ivar mode: 'query' or 'update'
    :ivar debug: True if debugging is active
    :ivar typedLiterals: True if INSERT should be done with typedLiterals
    :ivar profile(boolean): True if profiling / timing information should be displayed
    :ivar sparql: the SPARQLWrapper2 instance to be used
    '''
    def __init__(self,url,mode='query', debug=False, typedLiterals=False,  profile=False):
        '''
        Constructor a SPARQL wrapper
        
        Args:
            url(string): the base URL of the endpoint - the mode query/update is going to be appended
            mode(string): 'query' or 'update'
            debug(bool): True if debugging is to be activated
            typedLiterals(bool): True if INSERT should be done with typedLiterals
            profile(boolean): True if profiling / timing information should be displayed
        '''
        self.url="url%s" % (mode)
        self.mode=mode
        self.debug=debug
        self.typedLiterals=typedLiterals
        self.profile=profile
        self.sparql=SPARQLWrapper2(url)
        
    def rawQuery(self,queryString,method='POST'):
        '''
        query with the given query string
        
        Args:
            queryString(string): the SPARQL query to be performed
            method(string): POST or GET - POST is mandatory for update queries
        Returns:
            list: the raw query result as bindings
        '''
        self.sparql.setQuery(queryString)
        self.sparql.method=method
        queryResult = self.sparql.query()
        return queryResult 
    
    def getResults(self,jsonResult):
        '''
        get the result from the given jsonResult
        
        Args:
            jsonResult: the JSON encoded result
            
        Returns:
            list: the list of bindings
        '''    
        return jsonResult.bindings
    
    def insert(self,insertCommand):
        '''
        run an insert
        
        Args:
            insertCommand(string): the SPARQL INSERT command
          
        Returns:
            a response
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
        
        Args:
            name(string): the name to convert 
        
        Returns:
            string: a valid local name
        '''
        localName=''.join(ch for ch in name if ch.isalnum())
        return localName
    
    def insertListOfDicts(self,listOfDicts,entityType,primaryKey,prefixes,limit=None,batchSize=None, profile=False):
        '''
        insert the given list of dicts mapping datatypes 
        
        Args:
            entityType(string): the entityType to use as a 
            primaryKey(string): the name of the primary key attribute to use
            prefix(string): any PREFIX statements to be used
            limit(int): maximum number of records to insert
            batchSize(int): number of records to send per request
            
        Return:
            a list of errors which should be empty on full success
        
        datatype maping according to
        https://www.w3.org/TR/xmlschema-2/#built-in-datatypes
        
        mapped from 
        https://docs.python.org/3/library/stdtypes.html
        
        compare to
        https://www.w3.org/2001/sw/rdb2rdf/directGraph/
        http://www.bobdc.com/blog/json2rdf/
        https://www.w3.org/TR/json-ld11-api/#data-round-tripping
        https://stackoverflow.com/questions/29030231/json-to-rdf-xml-file-in-python
        '''
        if limit is not None:
            listOfDicts=listOfDicts[:limit]
        else:
            limit=len(listOfDicts)    
        total=len(listOfDicts)
        if batchSize is None:
            return self.insertListOfDictsBatch(listOfDicts, entityType, primaryKey, prefixes,total=total)
        else:
            startTime=time.time()
            errors=[]
            # store the list in batches
            for i in range(0, total, batchSize):
                recordBatch=listOfDicts[i:i+batchSize]
                batchErrors=self.insertListOfDictsBatch(recordBatch, entityType, primaryKey, prefixes,batchIndex=i,total=total,startTime=startTime)
                errors.extend(batchErrors)
            if self.profile:
                print("insertListOfDicts for %9d records in %6.1f secs" % (len(listOfDicts),time.time()-startTime))
            return errors    
       
    def insertListOfDictsBatch(self,listOfDicts,entityType,primaryKey,prefixes,title='batch',batchIndex=None,total=None,startTime=None):                
        '''
        insert a Batch part of listOfDicts
        
        Args:
            entityType(string): the entityType to use as a 
            primaryKey(string): the name of the primary key attribute to use
            prefix(string): any PREFIX statements to be used
            title(string): the title to display for the profiling (if any)
            batchIndex(int): the start index of the current batch
            total(int): the total number of records for all batches
            starttime(datetime): the start of the batch processing
            
        Return:
            a list of errors which should be empty on full success
        '''
        errors=[]
        size=len(listOfDicts)
        if batchIndex is None:
            batchIndex=0    
        batchStartTime=time.time()
        if startTime is None:
            startTime=batchStartTime
        insertCommand='%s\nINSERT DATA {\n' % prefixes
        for index,record in enumerate(listOfDicts):
            if not primaryKey in record:
                errors.append("missing primary key %s in record %d" % (primaryKey,index))
            else:    
                primaryValue=record[primaryKey]
                encodedPrimaryValue=self.getLocalName(primaryValue)
                tSubject="%s__%s" %(entityType,encodedPrimaryValue)
                for keyValue in record.items():
                    key,value=keyValue
                    valueType=type(value)
                    if self.debug:
                        print("%s(%s)=%s" % (key,valueType,value))
                    tPredicate="%s_%s" % (entityType,key)
                    tObject=value    
                    if valueType == str:   
                        tObject='"%s"' % value.replace('"','\\"')
                    elif valueType==int:
                        if self.typedLiterals:
                            tObject='"%d"^^<http://www.w3.org/2001/XMLSchema#integer>' %value
                        pass
                    elif valueType==float:
                        if self.typedLiterals:
                            tObject='"%s"^^<http://www.w3.org/2001/XMLSchema#decimal>' %value
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
                        insertRecord='  %s %s %s.\n' % (tSubject,tPredicate,tObject)
                        insertCommand+=insertRecord
        insertCommand+="\n}"
        if self.debug:
            print (insertCommand)
        self.insert(insertCommand)
        if self.profile:    
            print("%7s for %9d - %9d of %9d %s in %6.1f s -> %6.1f s" % (title,batchIndex+1,batchIndex+size,total,entityType,time.time()-batchStartTime,time.time()-startTime))    
        return errors

    def query(self,queryString,method=POST):
        '''
        get a list of results for the given query
        
        Args:
            queryString(string): the SPARQL query to execute
            method(string): the method eg. POST to use
            
        Returns:
            list: list of bindings
        '''
        queryResult=self.rawQuery(queryString,method=method) 
        jsonResult=queryResult.convert()
        return self.getResults(jsonResult)
    
    def queryAsListOfDicts(self,queryString):
        '''
        get a list of dicts for the given query (to allow round-trip results for insertListOfDicts)
        
        Args:
            queryString(string): the SPARQL query to execute
            
        Returns:
            list: a list ofDicts
        '''
        records=self.query(queryString)
        listOfDicts=self.asListOfDicts(records)
        return listOfDicts
    
    def asListOfDicts(self,records):
        '''
        convert SPARQL result back to python native
        
        Args:
            record(list): the list of bindings
            
        Returns:
            list: a list of Dicts
        '''
        resultList=[]
        for record in records:
            resultDict={}
            for keyValue in record.items():
                key,value=keyValue
                datatype=value.datatype
                if datatype is not None:
                    if datatype=="http://www.w3.org/2001/XMLSchema#integer":
                        resultValue=int(value.value) 
                    elif datatype=="http://www.w3.org/2001/XMLSchema#decimal":
                        resultValue=float(value.value)     
                    elif datatype=="http://www.w3.org/2001/XMLSchema#boolean":
                        resultValue=value.value in ['TRUE','true']    
                    elif datatype=="http://www.w3.org/2001/XMLSchema#date":
                        dt=datetime.datetime.strptime(value.value,"%Y-%m-%d")  
                        resultValue=dt.date()  
                    else:
                        # unsupported datatype
                        resultValue=value.value      
                else:
                    resultValue=value.value  
                resultDict[key]=resultValue
            resultList.append(resultDict)
        return resultList
    
    def printErrors(self,errors):
        '''
        print the given list of errors
        
        Args:
            errors(list): a list of error strings
            
        Returns:
            boolean: True if the list is empty else false
        '''
        if len(errors)>0:
            print("ERRORS:")
            for error in errors:
                print(error)
            return True
        else:
            return False    