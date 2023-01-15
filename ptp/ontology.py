'''
Created on 2020-09-03

@author: wf
'''
from wikibot.smw import SMWBot
from wikibot.wikibot import WikiBot
from lodstorage.jsonable import JSONAble
from storage.entity import EntityManager

class Ontology(object):
    '''
    Ontology to be read from Semantic MediaWiki
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
| ?SchemaProperty iri = iri
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
        self.smw=SMWBot(self.wikibot.site)
        askResult=self.smw.query(ask)
        if self.debug:
            for askRecord in askResult.values():
                print(askRecord)
        return askResult
    
    def getPropertyRecords(self,wikiId):
        '''
        get the schema properties from the given wikId
        Args:
            wikiId(string): the wiki to get the property records from
        '''
        ask=self.getAsk("Concept:SchemaProperty")
        propRecords=self.fromWiki(wikiId, ask)
        return propRecords
    
    def getSchemaProperties(self,wikiId):
        '''
        get the schema properties from the given wikId
        Args:
            wikiId(string): the wiki to get the property records from
        '''
        propRecords=self.getPropertyRecords(wikiId)
        schemas=SchemaManager()
        schemas.fromProps(propRecords.values())
        return schemas
    
    def getRQSchema(self,fromCache=True):
        ''' 
        get the Requirements Wiki Schema
        '''
        schemaManager=SchemaManager()
        if fromCache and schemaManager.isCached():
            schemaManager.fromStore()
        else:
            propRecords=self.getPropertyRecords("rq")
            schemaManager.fromProps(propRecords.values())
            allProps=schemaManager.allProperties()
            schemaManager.store(allProps,sampleRecordCount=len(allProps))
        return schemaManager
   
class SchemaManager(JSONAble,EntityManager):
    '''
    manager for Schemas
    '''   
    def __init__(self,baseUrl='https://rq.bitplan.com/index.php',debug=False):
        self.debug=debug
        self.baseUrl=baseUrl
        self.schemasByName={}
        EntityManager.__init__(self,"Schemas",entityName="Property",entityPluralName="Properties",debug=debug)
        self.config.tableName="Property_rq" 
        
    def allProperties(self):
        '''
        get a list of Dict of all properties
        '''
        allProps=[]
        for schema in self.schemasByName.values():
            for prop in schema.propsById.values():
                allProps.append(prop.__dict__)
        return allProps
    
    def fromStore(self):
        '''
        restore me
        '''
        listOfProps=super().fromStore()
        self.fromProps(listOfProps)
        return listOfProps
     
    def fromProps(self,propRecords):
        '''
        get a dict of schemas for the given props
        '''
       
        for propRecord in propRecords:
            prop=Property(propRecord)
            if prop.schema in self.schemasByName:
                schema=self.schemasByName[prop.schema]
            else:
                schema=Schema(prop.schema)
                self.schemasByName[prop.schema]=schema
            schema.add(prop)    
        return self.schemasByName    

class Schema(JSONAble):
    '''
    an Ontology schema
    '''
    
    def __init__(self,name):
        '''
        initialize me from the given property records
        '''
        self.name=name
        self.propsById={}
        self.propsByName={}
        
    def add(self,prop):
        '''
        add the given property
        '''
        self.propsById[prop.id]=prop
        self.propsByName[prop.name]=prop
          
                
class Property(JSONAble):
    '''
    a single property
    '''
    
    def __init__(self,prop):
        '''
        construct me from the given schema property
        '''
        self.id=prop['id']
        self.iri=prop['iri']
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
            