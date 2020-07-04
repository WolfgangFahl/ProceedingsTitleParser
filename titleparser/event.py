'''
Created on 04.07.2020

@author: wf
'''
import json

class Event(object):
    '''
    an Event
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def fromAskResult(self,askRecord):
        ''' initialize me from the given ask result'''
        d=self.__dict__
        for key in ["city","homepage","country","creation_date","modification_date"]:
            if key in askRecord:
                d[key]=askRecord[key]
            else:
                d[key]=None    
        pass    
    
    def asJson(self):
        ''' return me as a JSON record 
        https://stackoverflow.com/a/36142844/1497139 '''
        return json.dumps(self.__dict__,indent=4,sort_keys=True, default=str)
        
    
    def __str__(self):
        ''' create a string representation of this title '''
        text=self.homepage
        return text
