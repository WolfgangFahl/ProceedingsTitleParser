'''
Created on 2020-08-10

@author: wf
'''
import pydgraph
import json
import time

class Dgraph(object):
    '''
    wrapper for https://dgraph.io/ GraphQL database
    '''

    def __init__(self, host='localhost',port=9080, debug=False,profile=False):
        '''
        Constructor
        '''
        self.host=host
        self.port=port
        
        self.debug=debug
        self.profile=profile
        self.client_stub = pydgraph.DgraphClientStub('%s:%d' % (host,port))
        self.client =pydgraph.DgraphClient(self.client_stub)
        
    def addSchema(self,schema):
        '''
        add the given schema
        '''
        result=self.client.alter(pydgraph.Operation(schema=schema))
        return result
    
    def addData(self,obj=None,nquads=None,limit=None, batchSize=None):
        '''
        add the given object/list of objects or nquads if  both are given nquads are ignored
        '''
        itemList=obj
        if itemList is None:
            return self.addDataTxn(obj=None,nquads=nquads,itemTitle="nquads")
        else:         
            if type(itemList) is not list:
                return self.addDataTxn(obj=obj)
            else:    
                if limit is not None:
                    itemList=itemList[:limit]
                else:
                    limit=len(itemList)    
                if batchSize is None:
                    return self.addDataTxn(obj=itemList)
                else:
                    startTime=time.time()
                    responses=[]
                    # store the list in batches
                    size=len(itemList)
                    for i in range(0, size, batchSize):
                        itemBatch=itemList[i:i+batchSize]
                        response=self.addDataTxn(obj=itemBatch, title="batch",index=i,total=size,startTime=startTime)
                        responses.append(response)
                    if self.profile:
                        print("addData for %9d items in %6.1f secs" % (len(itemList),time.time()-startTime))
                    return responses
        
    def addDataTxn(self,obj=None,nquads=None,index=None,total=None,title="addData",itemTitle="items",startTime=None):    
        response=None
        # Create a new transaction.
        txn = self.client.txn()
        
        try:
            itemList=obj
            size=1
            if index is None:
                index=0    
            batchStartTime=time.time()
            if startTime is None:
                startTime=batchStartTime
            # Run mutation.
            if itemList is not None:
                # check whether obj is  a list of items 
                # if do a mutation for every item in the list
                if type(itemList) is list:
                    size=len(itemList)
                    for item in itemList:
                        txn.mutate(set_obj=item)
                else:        
                    # single object
                    response = txn.mutate(set_obj=obj)
                if total is None:
                    total=size    
                if self.profile:    
                    print("%7s for %9d - %9d of %9d %s in %6.1f s -> %6.1f s" % (title,index+1,index+size,total,itemTitle,time.time()-batchStartTime,time.time()-startTime))    
            if nquads is not None:
                response = txn.mutate(set_nquads=nquads)    
            # Commit transaction.
            txn.commit()
        finally:
            if self.debug:
                print(itemList)
            # Clean up. Calling this after txn.commit() is a no-op and hence safe.
            txn.discard()
        return response
    
    def mutate(self,mutation):
        # Create a new transaction.
        txn = self.client.txn()
        return txn.mutate(mutation=mutation,commit_now=True)
        
    def query(self,graphQuery):
        '''
        do a query 
        '''
        response = self.client.txn(read_only=True).query(graphQuery)
        if self.debug:
            print (response.json.decode())
        result = json.loads(response.json)
        return result
        
    def drop_all(self):
        ''' Drop All - discard all data and start from a clean state.'''
        return self.client.alter(pydgraph.Operation(drop_all=True))
    
    def close(self):
        ''' close the client '''
        self.client_stub.close()
        