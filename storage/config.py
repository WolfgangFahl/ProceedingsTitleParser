'''
Created on 2020-08-29

@author: wf
'''
from enum import Enum

class StoreMode(Enum):
    '''
    possible supported storage modes
    '''
    JSON = 1
    SQL = 2
    SPARQL = 3
    DGRAPH = 4
    
class StorageConfig(object):
    '''
    a storage configuration
    '''

    def __init__(self, mode=StoreMode.SQL,cacheFile=None,withShowProgress=True,profile=True,debug=False,errorDebug=True):
        '''
        Constructor
        
        Args:
            mode(StoreMode): the storage mode e.g. sql
            cacheFile(string): the common cacheFile to use (if any)
            withShowProgress(boolean): True if progress should be shown
            profile(boolean): True if timing / profiling information should be shown
            debug(boolean): True if debugging information should be shown
            errorDebug(boolean): True if debug info should be provided on errors (should not be used for production since it might reveal data)
        '''
        self.mode=mode
        self.cacheFile=cacheFile
        self.profile=profile
        self.withShowProgress=withShowProgress
        self.debug=debug
        self.errorDebug=errorDebug
        
    @staticmethod
    def getDefault(debug=False):
        return StorageConfig.getSQL(debug)    
        
    @staticmethod
    def getSQL(debug=False):
        config=StorageConfig(mode=StoreMode.SQL,debug=debug)
        config.tableName=None
        return config
    
    @staticmethod
    def getJSON(debug=False):
        config=StorageConfig(mode=StoreMode.JSON,debug=debug)
        return config
    
    @staticmethod
    def getSPARQL(debug=False,endpoint='http://localhost:3030/cr',host='localhost'):
        config=StorageConfig(mode=StoreMode.SPARQL,debug=debug)
        config.host=host
        config.endpoint=endpoint
        config.prefix="PREFIX cr: <http://cr.bitplan.com/>"
        return config
    
    @staticmethod
    def getDgraph(debug=False,host='localhost'):
        config=StorageConfig(mode=StoreMode.DGRAPH,debug=debug)
        config.host=host
    
    