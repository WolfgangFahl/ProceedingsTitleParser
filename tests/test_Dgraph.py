'''
Created on 2020-08-11

@author: wf
'''
import unittest
from dg.dgraph import Dgraph

class TestDdgraph(unittest.TestCase):
    '''
    test Dgraph database 
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDgraph(self):
        cg=Dgraph(debug=True)
        cg.drop_all()
        schema='''
        name: string @index(exact) .
        weight: float .
        height: float .
type Pokemon {
   name
   weight
   height
}'''
        cg.addSchema(schema)
        pokemonList=[{'name':'Pikachu', 'weight':  6, 'height': 0.4 },
                  {'name':'Arbok',   'weight': 65, 'height': 3.5 }, 
                  {'name':'Raichu',  'weight': 30, 'height': 0.8 }, 
                  {'name':'Sandan',  'weight': 12, 'height': 0.6 }]
        cg.addData(obj=pokemonList)
        graphQuery='''{
# list of pokemons
  pokemons(func: has(name)) {
    name
    weight
    height
  }
}'''
        queryResult=cg.query(graphQuery)
        self.assertTrue('pokemons' in queryResult)
        pokemons=queryResult['pokemons']
        self.assertEqual(4,len(pokemons))
        cg.close()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()