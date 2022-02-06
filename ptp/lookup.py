'''
Created on 2020-07-06

@author: wf
'''
import os
import yaml

class Lookup(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def getExamples():
        path=os.path.dirname(__file__)
        examplesPath=path+"/../examples.yaml"
        with open(examplesPath, 'r') as stream:
            examples = yaml.safe_load(stream)
        return examples