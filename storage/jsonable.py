'''
Created on 2020-09-03

@author: wf
'''
import json

class JSONAble(object):
    '''
    mixin to allow classes to be JSON serializable see
    https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    def getValue(self,v):
        if (hasattr(v, "asJSON")):
            return v.asJSON()
        elif type(v) is dict:
            return self.reprDict(v)
        elif type(v) is list:
            vlist=[]
            for vitem in v:
                vlist.append(self.getValue(vitem))
            return vlist
        else:   
            return v
    
    def reprDict(self,srcDict):
        '''
        get my dict elements
        '''
        d = dict()
        for a, v in srcDict.items():
            d[a]=self.getValue(v)
        return d
    
    def asJSON(self):
        '''
        recursively return my dict elements
        '''
        return self.reprDict(self.__dict__)    