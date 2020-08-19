'''
Created on 2020-07-05

@author: wf
'''
import habanero
from ptp.event import EventManager
import json
import os
import glob

class Crossref(object):
    '''
    Access to Crossref's search api see https://github.com/CrossRef/rest-api-doc
    '''

    def __init__(self, debug=False,profile=False,mode='sparql',host=None,endpoint=None):
        '''
        Constructor
        '''
        self.cr=habanero.Crossref()
        self.debug=debug
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.em=EventManager('crossref',url='https://www.crossref.org/',title='crossref.org',profile=profile,debug=debug,mode=mode)
        
    def cacheEvents(self):
        for jsonFilePath in self.jsonFiles():
            print (jsonFilePath)
        pass
    
    def jsonFiles(self):
        jsonFiles=sorted(glob.glob(self.jsondir+"crossref-*.json"))
        return jsonFiles
    
    def fromJsonFile(self,jsonFilePath):
        with open(self.jsonFilePath) as jsonFile:
            eventBatch=json.load(jsonFile)    
        return eventBatch    
        
    def doiMetaData(self,doi):
        ''' get the meta data for the given doi '''
        metadata=None
        response=self.cr.works([doi])
        if 'status' in response and 'message' in response and response['status']=='ok':
            metadata=response['message']
        return metadata