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
        self.dbs = self.get_db_session(db_url)
        
    def get_db_session(self, db_url):
        "connect to the database and get a session"
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        return self.Session()

    def fields_to_dict(self, field_args):
        "convert command line field arguments into a dictionary"
        field_dict = {}
        for field in field_args:
            key, value = field.split(':')
            field_dict[key] = value
        return field_dict

    def normalize_name(self, name):
        "convert underscores to spaces and use title case"
        
        name = name.replace('_',' ').title()
        return name
    

    def search(self, field_args):
        "search for pets from args, print a list of pets"
        
        filter_dict = self.fields_to_dict(field_args)
        print "Searching with search arguments: %s" % filter_dict
        pets = self.get_pets(filter_dict)
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
        print output     
   

    def add_pet(self, field_args):
        "add a new pet to the db, creating breed, species, & shelter if need be"

        print "Adding pet to database: %s" % field_args
        fields = self.fields_to_dict(field_args)
        # fields is a dict of key value pairs
        if 'species' in fields:
            species_name= self.normalize_name( fields.pop('species') )
            # check if species is in db, if not, add it
            species = self.dbs.query(Species).filter(Species.name==species_name).first()
            if not species:
                species = Species(name=species_name)
                self.dbs.add(species)
        else:
            species = None
        # replace the value in the fields dict with the SQLA species obj or None
        fields['species'] = species

        if 'breed' in fields:
            breed_name = self.normalize_name( fields.pop('breed') )
            # check if this breed is already in the db
            breed = self.dbs.query(Breed).filter(Breed.name==breed_name).first()
            if not breed:
                # add the breed, but *only* if we got a species
                if species:
                    breed = Breed(name=breed_name, species=species)
                    self.dbs.add(Breed)
        else:
            breed = None
        # replace the value in the fields dict with the SQLA species obj or None
        fields['breed'] = breed

        if 'shelter' in fields:
            # check if this shelter is in db, if not, add it
            shelter = self.dbs.query(Shelter).filter(
                Shelter.name==fields['shelter'] ).first()
            if not shelter:
                shelter = Shelter(name=fields['shelter'])
                self.dbs.add(shelter)
        else:
            shelter = None
        fields['shelter'] = shelter

        # make sure our input for adopted, dead, and age are valid
        try:
            if 'age' in fields:
                fields['age'] = int( fields['age'] )
        except:
            fields.pop('age')

        for bool_field in 'adopted', 'dead':
            try:
                if bool_field in fields:
                    fields[bool_field] = bool( fields[bool_field] )
            except:
                fields.pop(bool_field)
        
        # fields dict is now validated and converted.
        # use dict expansion to make our pet
        new_pet = Pet()
        for attr,value in fields.items():
            if hasattr(Pet, attr):
                setattr(new_pet, attr, value)
        self.dbs.add( new_pet )
        self.dbs.commit()
        print "New pet created."



    def get_pets(self, filter_dict):
        "return a list of Pet objects for a filter dict"
        
        # make our base query
        query = self.dbs.query(Pet)
        # filter for breed
        if 'breed' in filter_dict:
            query = query.join(Breed)
            # convert "labrador_retriever" to "Labrador Retriever"
            # we use dict.pop to remove the item from the dict
            breed_name = self.normalize_name( filter_dict.pop('breed') )
            query = query.filter(Breed.name==breed_name)

        # only filter on species if not filtering on breed
        if 'species' in filter_dict and 'breed' not in filter_dict:
            query = query.join(Breed).join(Species)
            species_name = self.normalize_name( filter_dict.pop('species') )
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

    db_url = "postgresql:///pets"
    # instantiate an instance of our PetApp  
    PetApp = PetApp(db_url=db_url)
    
    # call the pet app to either add a pet or search for pets
    if args.add:
        PetApp.add_pet(args.fields)
    else:
        PetApp.search(args.fields)

