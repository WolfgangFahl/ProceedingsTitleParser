'''
Created on 2020-08-11

@author: wf
'''
import urllib.request
import json
import os
import time
import ptp.openresearch
from lodstorage.sparql import SPARQL
from lodstorage.entity import EntityManager
from lodstorage.storageconfig import StoreMode, StorageConfig

class CityManager(EntityManager):
    ''' manage cities '''

    def __init__(self,name,config=None):
        '''
        constructor

        Args:
            name(string): the name of this city Manager
        '''
        if config is None:
            config=StorageConfig.getSQL()
        config.tableName="City_%s" % name
        self.cityList=None
        super().__init__(name,entityName="City",entityPluralName="Cities",config=config)
        pass

    def getListOfDicts(self):
        '''
        get the list of Dicts for this city manager
        '''
        if self.cityList is None:
            self.fromWikiData(self.endpoint)
        return self.cityList

    def fromCache(self):
        self.cityList=super().fromCache()
        return self.cityList

    def fromLutangar(self):
        '''
        get city list provided by Johan Dufour https://github.com/lutangar
        '''
        cityJsonUrl="https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json"
        with urllib.request.urlopen(cityJsonUrl) as url:
            self.cityList=json.loads(url.read().decode())
    

    def fromOpenResearch(self,limit=10000,batch=500,showProgress=False):
        '''
        get cities from open research
        '''
        cities=[]
        smw=ptp.openresearch.OpenResearch.getSMW()
        offset=0
        startTime=time.time()
        while True:
            ask="""{{#ask: [[Has_location_city::+]][[isA::Event]]
    |?Has_location_city=city
    | limit = %d
    | offset = %d
    }}""" % (batch,offset)
            askResult=smw.query(ask)
            found=len(askResult.values())
            if showProgress:
                print("retrieved cities %5d-%5d after %5.1f s" % (offset+1,offset+found,time.time()-startTime))
            for askRecord in askResult.values():
                cityValue= askRecord['city']
                if type(cityValue) is list:
                    for cityEntry in cityValue:
                        cities.append(cityEntry)
                else:
                    cities.append(cityValue)
            offset=offset+batch
            if found<batch or len(cities)>=limit:
                    break
        return cities

    def fromWikiData(self,endpoint):
        '''
        get the city List from WikiData

        Args:
            endpoint(string): the url of the endpoint to be used

        Returns:
            list: and sets it as self.cityList as a side effect
        '''
        wd=SPARQL(endpoint)
        queryString="""# get a list of cities
# for geograpy3 library
# see https://github.com/somnathrakshit/geograpy3/issues/15
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
# get human settlements
SELECT DISTINCT ?city ?cityLabel (max(?cityPop) as ?cityPopulation) (min (?coord) as ?cityCoord) ?region ?regionLabel ?regionIsoCode ?country ?countryLabel ?countryIsoCode ?countryPopulation ?countryGdpPerCapita WHERE {
  # if you uncomment this line this query might run for some 3 hours on a local wikidata copy using Apache Jena
  # run for Vienna, Illinois, Vienna Austria, Paris Texas and Paris France as example only
  # VALUES ?city { wd:Q577544 wd:Q1741 wd:Q830149 wd:Q90}.
  # run for Andorra Q228 
  # VALUES ?country {wd:Q228}.
  # instance of human settlement https://www.wikidata.org/wiki/Q486972
  ?city wdt:P31/wdt:P279* wd:Q486972 .
  # label of the City
  ?city rdfs:label ?cityLabel filter (lang(?cityLabel) = "en").
  # country this city belongs to
  ?city wdt:P17 ?country .
  # label for the country
  ?country rdfs:label ?countryLabel filter (lang(?countryLabel) = "en").
  # https://www.wikidata.org/wiki/Property:P297 ISO 3166-1 alpha-2 code
  ?country wdt:P297 ?countryIsoCode.
  # population of country
  ?country wdt:P1082 ?countryPopulation.
  OPTIONAL {
     ?country wdt:P2132 ?countryGdpPerCapita.
  }
  OPTIONAL {
     # located in administrative territory
     # https://www.wikidata.org/wiki/Property:P131
     ?city wdt:P131* ?region.
     # administrative unit of first order
     ?region wdt:P31/wdt:P279* wd:Q10864048.
     ?region rdfs:label ?regionLabel filter (lang(?regionLabel) = "en").
     # isocode state/province
     OPTIONAL { ?region wdt:P300 ?regionIsoCode. }
  }
  # population of city
  OPTIONAL { ?city wdt:P1082 ?cityPop.}
   # get the coordinates
  OPTIONAL { ?city wdt:P625 ?coord. }
} GROUP BY  ?city ?cityLabel  ?cityCoord ?region ?regionLabel ?regionIsoCode ?country ?countryLabel ?countryIsoCode ?countryPopulation ?countryGdpPerCapita
#ORDER BY ?cityLabel
"""
        results=wd.query(queryString)
        self.cityList=wd.asListOfDicts(results)
        for city in self.cityList:
            city['wikidataurl']=city.pop('city')
            city['name']=city.pop('cityLabel')
            super().setNone(city,['coord','date','cityPopulation','countryPopulation','country','countryLabel','countryIsoCode','countryGDP_perCapita','region','regionLabel','regionIsoCode','ratio'])
        return self.cityList

class ProvinceManager(EntityManager):
    '''
    manage province information
    '''
    def __init__(self,name,config=None,debug=False):
        '''
        Constructor
        '''
        if config is None:
            config=StorageConfig.getSQL()
        config.debug=debug
        config.tableName="Province_%s" % name
        self.provinceList=None
        super().__init__(name,entityName="Province",entityPluralName="Provinces",config=config)

    def getListOfDicts(self):
        '''
        get my list of dicts
        '''
        if self.provinceList is None:
            self.fromWikiData(self.endpoint)
        return self.provinceList

    def fromCache(self):
        self.provinceList=super().fromCache()
        return self.provinceList

    def fromWikiData(self,endpoint):
        '''
        get the province List from WikiData

        Args:
            endpoint(string): the url of the endpoint to be used
        Returns:
            list: and sets it as self.provinceList as a side effect
        '''
        wd=SPARQL(endpoint)
        queryString="""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT ?region ?isocc ?isocode4 ?regionLabel ?population ?location
WHERE
{
  # administrative unit of first order
  ?region wdt:P31/wdt:P279* wd:Q10864048.
  OPTIONAL {
     ?region rdfs:label ?regionLabel filter (lang(?regionLabel) = "en").
  }
  # filter historic regions
  # FILTER NOT EXISTS {?region wdt:P576 ?end}
  # get the population
  # https://www.wikidata.org/wiki/Property:P1082
  OPTIONAL { ?region wdt:P1082 ?population. }
  # # https://www.wikidata.org/wiki/Property:P297
  OPTIONAL { ?region wdt:P297 ?isocc. }
  # isocode state/province
  ?region wdt:P300 ?isocode4.
  # https://www.wikidata.org/wiki/Property:P625
  OPTIONAL { ?region wdt:P625 ?location. }
}
ORDER BY (?isocode4)
"""
        results=wd.query(queryString)
        self.provinceList=wd.asListOfDicts(results)
        for province in self.provinceList:
            province['wikidataurl']=province.pop('region')
            province['name']=province.pop('regionLabel')
            super().setNone(province,['population','location'])
        return self.provinceList

class CountryManager(EntityManager):
    ''' manage countries '''

    def __init__(self,name,config=None,debug=False):
        '''
        Constructor
        '''
        if config is None:
            config=StorageConfig.getSQL()
        config.debug=debug
        config.tableName="Country_%s" % name
        self.countryList=None
        path=os.path.dirname(__file__)
        super().__init__(name,entityName="Country",entityPluralName="Countries",config=config)

        self.sampledir=path+"/../sampledata/"
        self.schema='''
name: string @index(exact) .
code: string @index(exact) .
capital: string .
location: geo .
type Country {
   code
   name
   location
   capital
}'''
        self.graphQuery='''{
  # list of countries sorted by name
  countries(func: has(isocode),orderasc: name) {
    uid
    name
    isocode
    capital
    location
  }
}'''
    def getListOfDicts(self):
        '''
        get the list of Dicts for this city manager
        '''
        if self.countryList is None:
            self.fromWikiData(self.endpoint)
        return self.countryList

    def fromCache(self):
        self.countryList=super().fromCache()
        return self.countryList

    def fromConfRef(self):
        '''
        get countries from ConfRef
        '''
        confRefCountriesJsonFileName='%s/confref-countries.json' % self.sampledir
        with open(confRefCountriesJsonFileName) as confRefCountriesJson:
            self.confRefCountries=json.load(confRefCountriesJson)
        for country in self.confRefCountries:
            country['name']=country.pop('value')
        self.confRefCountries=sorted(self.confRefCountries, key = lambda c: c['name'])

    def fromErdem(self):
        '''
        get country list provided by Erdem Ozkol https://github.com/erdem
        '''
        countryJsonUrl="https://gist.githubusercontent.com/erdem/8c7d26765831d0f9a8c62f02782ae00d/raw/248037cd701af0a4957cce340dabb0fd04e38f4c/countries.json"
        with urllib.request.urlopen(countryJsonUrl) as url:
            self.countryList=json.loads(url.read().decode())
        mode=self.config.mode
        for country in self.countryList:
            # rename dictionary keys
            #country['name']=country.pop('Name')
            country['isocode']=country.pop('country_code')
            lat,lng=country.pop('latlng')
            country['location']={'type': 'Point', 'coordinates': [lng,lat] }

    def fromWikiData(self,endpoint):
        '''
        get the country List from WikiData

        Args:
            endpoint(string): the url of the endpoint to be used
         Returns:
            list: and sets it as self.countryList as a side effect
        '''
        wd=SPARQL(endpoint)
        queryString="""
# get a list countries with the corresponding ISO code
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
SELECT ?country ?countryLabel ?shortName (MAX(?pop) as ?population) ?gdpPerCapita ?coord ?isocode
WHERE
{
  # instance of country
  ?country wdt:P31 wd:Q3624078.
  OPTIONAL {
     ?country rdfs:label ?countryLabel filter (lang(?countryLabel) = "en").
   }
  OPTIONAL {
      ?country p:P1813 ?shortNameStmt. # get the short name statement
      ?shortNameStmt ps:P1813 ?shortName # the the short name value from the statement
      filter (lang(?shortName) = "en") # filter for English short names only
      filter not exists {?shortNameStmt pq:P31 wd:Q28840786} # ignore flags (aka emojis)
  }
  OPTIONAL {
    # get the population
     # https://www.wikidata.org/wiki/Property:P1082
     ?country wdt:P1082 ?pop.
  }
 OPTIONAL {
     # get the gross domestic product per capita
     ?country wdt:P2132 ?gdpPerCapita.
  }
  # get the iso countryCode
  { ?country wdt:P297 ?isocode }.
  # get the coordinate
  OPTIONAL { ?country wdt:P625 ?coord }.
}
GROUP BY ?country ?countryLabel ?shortName ?population ?gdpPerCapita ?coord ?isocode
ORDER BY ?countryLabel"""
        results=wd.query(queryString)
        self.countryList=wd.asListOfDicts(results)
        for country in self.countryList:
            country['wikidataurl']=country.pop('country')
            country['name']=country.pop('countryLabel')
            super().setNone(country,['shortName','gdpPerCapita'])
        return self.countryList

    def storeToRDF(self,sparql):
        '''
        store my country list to the given SPARQL store
        '''
        entityType="cr:Country"
        primaryKey="isocode"
        prefixes="PREFIX cr: <http://cr.bitplan.com/>"
        errors=sparql.insertListOfDicts(self.countryList, entityType, primaryKey, prefixes)
        return errors

    def fromRDF(self,sparql):
        '''
        restore me from the given sparql store
        '''
        countryQuery="""
PREFIX cr: <http://cr.bitplan.com/>
SELECT ?name ?population ?coord ?isocode ?wikidataurl WHERE {
    ?country cr:Country_name ?name.
    ?country cr:Country_population ?population.
    ?country cr:Country_coord ?coord.
    ?country cr:Country_isocode ?isocode.
    ?country cr:Country_wikidataurl ?wikidataurl.
}"""
        countryRecords=sparql.query(countryQuery)
        self.countryList=sparql.asListOfDicts(countryRecords)
