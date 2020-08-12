'''
Created on 2020-08-11

@author: wf
'''
import urllib.request
import json
import os
import time
import ptp.openresearch 

class Country(object):
    '''
    handle countries
    '''

    def __init__(self):
        '''
        Constructor
        '''

class CityManager(object):
    ''' manage cities '''
    
    def __init__(self):
        pass
    
    def fromLutangar(self):
        ''' 
        get city list provided by Johan Dufour https://github.com/lutangar
        '''
        cityJsonUrl="https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json"
        with urllib.request.urlopen(cityJsonUrl) as url:
            self.cityList=json.loads(url.read().decode())
        for city in self.cityList:
            city['dgraph.type']='City'
            lat=float(city['lat'])
            lng=float(city['lng'])
            city['location']={'type': 'Point', 'coordinates': [lng,lat] }   
            
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

class CountryManager(object):
    ''' manage countries '''
    
    def __init__(self):
        '''
        Constructor
        '''
        path=os.path.dirname(__file__)
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
        for country in self.countryList:
            # rename dictionary keys
            #country['name']=country.pop('Name')
            country['isocode']=country.pop('country_code')
            country['dgraph.type']='Country'
            lat,lng=country.pop('latlng')
            country['location']={'type': 'Point', 'coordinates': [lng,lat] }  