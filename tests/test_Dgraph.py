'''
Created on 2020-08-11

@author: wf
'''
import unittest
from storage.dgraph import Dgraph

class TestDdgraph(unittest.TestCase):
    '''
    test Dgraph database
    '''

    def setUp(self):
        self.active=False
        pass


    def tearDown(self):
        pass

    def testDgraph(self):
        '''
        test basic Dgraph operation
        '''
        if not self.active:
            return
        dgraph=Dgraph(debug=True)
        # drop all data and schemas
        dgraph.drop_all()
        # create a schema for Pokemons
        schema='''
        name: string @index(exact) .
        weight: float .
        height: float .
type Pokemon {
   name
   weight
   height
}'''
        dgraph.addSchema(schema)
        # prepare a list of Pokemons to be added
        pokemonList=[{'name':'Pikachu', 'weight':  6, 'height': 0.4 },
                  {'name':'Arbok',   'weight': 65, 'height': 3.5 },
                  {'name':'Raichu',  'weight': 30, 'height': 0.8 },
                  {'name':'Sandan',  'weight': 12, 'height': 0.6 }]
        # add the list in a single transaction
        dgraph.addData(obj=pokemonList)
        # retrieve the data via GraphQL+ query
        graphQuery='''{
# list of pokemons
  pokemons(func: has(name), orderasc: name) {
    name
    weight
    height
  }
}'''
        queryResult=dgraph.query(graphQuery)
        # check the result
        self.assertTrue('pokemons' in queryResult)
        pokemons=queryResult['pokemons']
        self.assertEqual(len(pokemonList),len(pokemons))
        sortindex=[1,0,2,3]
        for index,pokemon in enumerate(pokemons):
            expected=pokemonList[sortindex[index]]
            self.assertEqual(expected,pokemon)
        # close the database connection
        dgraph.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
