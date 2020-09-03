'''
Created on 2020-09-03

@author: wf
'''
from wikibot.smw import SMW
from wikibot.wikibot import WikiBot
from storage.jsonable import JSONAble

class Ontology(object):
    '''
    classdocs
    '''


    def __init__(self,debug=False):
        '''
        Constructor
        
        Args:
            debug(boolean): True if debugging should be switched on
        '''
        self.debug=debug
        
    def getAsk(self,condition,limit=1000,offset=0):    
        '''
        get the ask query for the given condition
        '''
        ask="""{{#ask: [[%s]]
| mainlabel=SchemaProperty
| ?SchemaProperty name = name
| ?SchemaProperty definition = definition
| ?SchemaProperty comment = comment
| ?SchemaProperty examples = examples
| ?SchemaProperty type = type
| ?SchemaProperty kind = kind
| ?SchemaProperty mapsTo = mapsTo
| ?SchemaProperty id = id
| ?SchemaProperty cardinality = cardinality
| ?SchemaProperty schema = schema
| ?Creation date = creation_date
| ?Modification date = modification_date
| limit = %d
| offset = %d
}}
""" % (condition,limit,offset)
        return ask    
        
    def fromWiki(self,wikiId,ask):
        '''
        get the ontology from the given wikiId
        Args:
            wikiId(string): the wikiId to get the ontology from
        Returns:
            the list of schema properties
        '''
        self.wikibot=WikiBot.ofWikiId(wikiId)
        self.smw=SMW(self.wikibot.site)
        askResult=self.smw.query(ask)
        if self.debug:
            for askRecord in askResult.values():
                print(askRecord)
        return askResult
    
    def getSchemaProperties(self,wikiId):
        '''
        get the schema properties
        '''
        ask=self.getAsk("Concept:SchemaProperty")
        propRecords=self.fromWiki(wikiId, ask)
        return Schema.fromProps(propRecords)

class Schema(JSONAble):
    '''
    an Ontology schema
    '''
    
    @staticmethod
    def fromProps(propRecords):
        '''
        get a dict of schemas for the given props
        '''
        schemasByName={}
        for propRecord in propRecords.values():
            prop=Property(propRecord)
            if prop.schema in schemasByName:
                schema=schemasByName[prop.schema]
            else:
                schema=Schema(prop.schema)
                schemasByName[prop.schema]=schema
            schema.add(prop)    
        return schemasByName
    
    def __init__(self,name):
        '''
        initialize me from the given property records
        '''
        self.name=name
        self.propsById={}
        
    def add(self,prop):
        '''
        add the given property
        '''
        self.propsById[prop.id]=prop
          
                
class Property(JSONAble):
    '''
    a single property
    '''
    
    def __init__(self,prop):
        '''
        construct me from the given schema property
        '''
        self.id=prop['id']
        self.name=prop['name']
        self.definition=prop['definition']
        self.comment=prop['comment']
        self.examples=prop['examples']
        self.kind=prop['kind']
        self.type=prop['type']
        self.mapsTo=prop['mapsTo']
        self.cardinality=prop['cardinality']
        self.schema=prop['schema']
        pass
            