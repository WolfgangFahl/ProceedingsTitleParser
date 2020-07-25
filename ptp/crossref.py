'''
Created on 2020-07-05

@author: wf
'''
import habanero

class Crossref(object):
    '''
    Access to Crossref's search api see https://github.com/CrossRef/rest-api-doc
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.cr=habanero.Crossref()
        
    def doiMetaData(self,doi):
        ''' get the meta data for the given doi '''
        metadata=None
        response=self.cr.works([doi])
        if 'status' in response and 'message' in response and response['status']=='ok':
            metadata=response['message']
        return metadata