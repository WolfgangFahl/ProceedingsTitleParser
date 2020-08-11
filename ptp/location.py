'''
Created on 2020-08-11

@author: wf
'''
import urllib.request
import json
import os

class Country(object):
    '''
    handle countries
    '''

    def __init__(self):
        '''
        Constructor
        '''

class CountryManager(object):
    
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