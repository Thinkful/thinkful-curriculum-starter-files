"unit tests for our pet app that do not use the database"
from pets_script import PetApp

import pdb

import unittest

class Mock(object):
    "a generic mock object"
    def __init__(self, **kwargs):
        for attr,val in kwargs.items():
            setattr(self, attr, val)


class MockPet(object):
    "a mock pet, has defaults for all pet attributes"
    def __init__(self, **kwargs):
        for attr in ['name','age','adopted','dead',
            'breed', 'species', 'shelter']:
            setattr(self, attr, kwargs.get(attr, None) )  


class PetAppUnitTests(unittest.TestCase):

    def test_search_output(self):
        "test_search_output - test the output formatting"
        mock_pets = [
            MockPet( name='Titchy', age=17, adopted=True, dead=True,
                breed=Mock( name='Tabby', species=Mock(name='Cat') ),
                shelter=Mock( name='BCSPCA' ) ),
            MockPet( name='Ginger', age=1, adopted=True, dead=False,
                breed=Mock( name='Labradoodle', species=Mock(name='Dog') ),
                shelter=Mock( name='BCSPCA' ) )
            ]
        
        output = PetApp.search_output(mock_pets)
        assert output
                
                
 
