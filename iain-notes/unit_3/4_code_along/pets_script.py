"""
pets_script.py 
- allows one to search for pets or add a pet
- called with list of field names in the format:
     name:Ginger breed:labrador_retreiver age:10
- prints out a list pets matching the search terms
- if called with -a or -add, instead creates a new pet
- when creating a new pet, values for breed, species and shelter
  should check of existing matching entires and use them,
  or create new ones if none exist
- the model should be stored in a separate file and imported
- the application should be created as an object that
  gets instantiated and then used from __main__
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Text

from sqlalchemy.orm import sessionmaker

import sys
import pdb
import argparse

from pets_model import (
    Species,
    Breed,
    Shelter,
    Pet,
    Person
)


class PetApp(object):

    def __init__(self, db_url):
        """
        Create and initialize the PetApp object, creates
        an sqlalchemy engine and session for the database.
        Initializes self._dbs, the SQLAlchemy session.
        param db_url: a db connection string
        """
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        self._dbs = Session()

    def __delete__(self):
        self.clean_up()

    def clean_up(self):
        self._dbs.close()

    def search(self, field_args):
        """
        Search for pets from a list of search terms.
        
        param field_list: a list of strings such as:
            ['name:titchy','breed:tabby']
        returns: string output from the search with pet details.
        """
        filter_dict = self._fields_to_dict(field_args)
        pets = self._get_pets(filter_dict)
        output = self._output_pet_list(pets)

        self.clean_up()
        return output


    def add_pet(self, field_args):
        """
        Add a new pet to the database. If a breed, shelter,
        or species is specified, create new ones if they 
        don't already exist.
        
        param field_list: a list of strings such as:
        side effects: creates a new pet, and possibly a new
           breed, species, and/or shelter.
        returns: string output with new pet details.
            ['name:titchy','breed:tabby']
        """
 
        # convert fields to a dict of key/val pairs 
        fields = self._fields_to_dict(field_args)
        
        # replace the value in the fields dict with the SQLA species obj or None
        fields['species'] = self._get_species( fields['species'] ) if \
            'species' in fields else None 
        
        fields['breed'] = self._get_breed( fields['breed'], species ) if \
            'breed' in fields else None 

        fields['shelter'] = self._get_shelter( fields['shelter'] ) if \
            'shelter' in fields else None
        # all our relations are now either None or SQLA objects
        
        pet = self._save_pet( fields )
        output = self._add_output(pet)
        
        self.clean_up()
        return output


    @staticmethod
    def _fields_to_dict(field_args):
        "convert command line field arguments into a dictionary"
        field_dict = {}
        for field in field_args:
            key, value = field.split(':')
            field_dict[key] = value
        return field_dict

    @staticmethod
    def _normalize_name(name):
        "convert underscores to spaces and use title case"
        name = name.replace('_',' ').title()
        return name

    def _get_species(self, species_arg):
        """
        convert a species string to an instantiated species object
        - optionally creates a new species in the db if need be
        """
        species_name = self._normalize_name( species_arg )
        species = self._dbs.query(Species).filter(Species.name==species_name).first()
        if not species:
            species = Species(name=species_name)
            self._dbs.add(species)
        return species


    def _get_breed(self, breed_arg, species=None):
        """
        convert a breed string to an instantiated breed object
        takes an optional species param
        optionally creates a new breed in the db if need be
        """
        breed_name = self._normalize_name( breed_arg )
        breed = self._dbs.query(Breed).filter(Breed.name==breed_name).first()
        # we can only make a new breed if we got a species arg
        if not breed and species != None:
            breed = Breed(name=breed_name, species=species)
            self._dbs.add(breed)
        # NB: we could be returning None for breed, that's ok
        return breed


    def _get_shelter(self, shelter_arg):
        """
        convert a shelter string to an instantiated shelter object
        - optionally creates a new shelter in the db if need be
        """
        # we use the shelter name as is, no normalizing
        shelter = self._dbs.query(Shelter).filter(
            Shelter.name==shelter_name).first()
        if not shelter:
            shelter = Shelter(name=shelter_name)
            self._dbs.add(shelter)
        return shelter


    @classmethod
    def _search_output(cls, pets):
        """
        create the string output from a list of pets
        param pets: a list of pet objects to display
        """
        # NB: this could be unit tested without the database
        # as we only need the pets param to contain objects with
        # the right attributes
        output = "Results of your pet search:\n"
        for pet in pets:
            output += ( "%s, age %s. Breed: %s, Species: %s, Shelter: %s" %
                (pet.name, pet.age, 
                pet.breed.name if pet.breed else "n/a", 
                pet.breed.species.name if pet.breed else "n/a",
                pet.shelter.name if pet.shelter else "n/a" ) )
            if not pet.adopted:
                output += " (this pet is available for adoption)"
            else: 
                output += " (adopted)"
            output += "\n"
        return output     


    @classmethod
    def _add_output(cls, pet):
        "create the string output for a new pet creation"
        output = ("New pet created. Name: %s Age: %s: Adopted: %s Shelter: %s"
            % (pet.name, pet.age, pet.adopted, pet.shelter) )
        return output


    def _save_pet(self, fields):
        """
        Persist a pet to the DB from a dict of values
        param fields: dict of field values for the new pet
        returns:  newly created pet
        side effects: new pet saved in database
        """
        new_pet = Pet()
        for attr,value in fields.items():
            if hasattr(Pet, attr):
                setattr(new_pet, attr, value)
        self._dbs.add( new_pet )
        self._dbs.commit()
        return new_pet 
            

    def _get_pets(self, filter_dict):
        "return a list of Pet objects for a filter dict"
        
        # make our base query
        query = self._dbs.query(Pet)
        # filter for breed
        if 'breed' in filter_dict:
            query = query.join(Breed)
            # convert "labrador_retriever" to "Labrador Retriever"
            # we use dict.pop to remove the item from the dict
            breed_name = self._normalize_name( filter_dict.pop('breed') )
            query = query.filter(Breed.name==breed_name)

        # only filter on species if not filtering on breed
        if 'species' in filter_dict and 'breed' not in filter_dict:
            query = query.join(Breed).join(Species)
            species_name = self._normalize_name( filter_dict.pop('species') )
            query = query.filter(Species.name == species_name) 
       
        # shelter
        if 'shelter' in filter_dict:
            query = query.join(Shelter)
            query = query.filter(Shelter.name == filter_dict.pop('shelter') )

        # other fields (name, age, dead, adopted)    
        for field_name, field_value in filter_dict.items():
            if hasattr(Pet, field_name):
                query = query.filter( getattr(Pet, field_name) == field_value)

        # now execute our query
        pets = query.all()
        return pets



################################################################################
if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Pet Shelter Searching App')
    
    parser.add_argument('fields', metavar='fields', type=str, nargs='+',
        help='List of string fields in the form "age:12". '
        'Use underscores for spaces, IE "breed:labrador_retriever"')
    parser.add_argument("-a", "--add", action="store_true",
        help="Add a new pet instead of searching")
    args = parser.parse_args()

    # this could come from a command line arg or an ENV variable
    db_url = "postgresql:///pets"

    # instantiate an instance of our PetApp  
    pet_app = PetApp(db_url=db_url)
    
    # call the pet app to either add a pet or search for pets
    if args.add:
        output = pet_app.add_pet(args.fields)
        print output
    else:
        output = pet_app.search(args.fields)
        print output
