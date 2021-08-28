'''
Created on 2021-08-28

@author: wf
'''
from corpus.event import Event
import html
import re

class ParsedEvent(Event):
    '''
    a scientific event derived by parsing a Conference Reference
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def fromTitle(self,title,debug=False):
        ''' 
        fill my data from the given Title 
        Args:
            title(Title): the title to get the information from
            debug(boolean): True if debugging should be activated
        '''
        md=title.metadata()
        # See CrossRef.fixEncodings if needed
        #Event.fixEncodings(md,debug)
        self.fromDict(md)
        self.getLookupAcronym()
            
    def fromDict(self,srcDict,withHtmlUnescape=False):
        ''' 
        fill my data from the given source Dict
        Args:
            srcDict(dict): the dict to fill my data from
            withHtmlUnescape(boolean): True if HTML entities should be unescaped e.g. Montr&#233;al
        '''
        d=self.__dict__
        for key in srcDict:
            targetKey=key
            if key=="id":
                targetKey='eventId'
            value=srcDict[key]
            if withHtmlUnescape and value is not None and type(value) is str:
                value=html.unescape(value)
            d[targetKey]=value        
        self.getLookupAcronym()         
    
    def getLookupAcronym(self):
        ''' get the lookup acronym of this event e.g. add year information '''
        if hasattr(self,'acronym') and self.acronym is not None:
            self.lookupAcronym=self.acronym
        else:
            if hasattr(self,'event'):
                self.lookupAcronym=self.event
        if hasattr(self,'lookupAcronym'):
            if self.lookupAcronym is not None:
                try:
                    if hasattr(self, 'year') and self.year is not None and not re.search(r'[0-9]{4}',self.lookupAcronym):
                        self.lookupAcronym="%s %s" % (self.lookupAcronym,str(self.year))
                except TypeError as te:
                    print ('Warning getLookupAcronym failed for year: %s and lookupAcronym %s' % (self.year,self.lookupAcronym))   
    
        