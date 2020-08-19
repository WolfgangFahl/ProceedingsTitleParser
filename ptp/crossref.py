'''
Created on 2020-07-05

@author: wf
'''
import habanero
from ptp.event import EventManager

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
        self.em=EventManager('crossref',url='https://www.crossref.org/',title='crossref.org',profile=profile,debug=debug,mode=mode)
        
    def doiMetaData(self,doi):
        ''' get the meta data for the given doi '''
        metadata=None
        response=self.cr.works([doi])
        if 'status' in response and 'message' in response and response['status']=='ok':
            metadata=response['message']
        return metadata