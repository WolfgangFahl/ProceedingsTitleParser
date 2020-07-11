'''
Created on 2020-07-11

@author: wf
'''
from ptp.event import EventManager
import os
import json

class ConfRef(object):
    '''
    classdocs
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.em=EventManager('confref')
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.jsonFilePath=self.jsondir+"confref-conferences.json"
        
    def initEventManager(self):
        ''' initialize me from my json file '''
        with open(self.jsonFilePath) as jsonFile:
            self.rawevents=json.load(jsonFile)
        
        