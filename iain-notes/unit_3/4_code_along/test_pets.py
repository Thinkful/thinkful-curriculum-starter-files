# tests for the code-along
import unittest

from pets_model import (
    pet_person_table,
    Base,
    Species,
    Breed,
    Pet,
    Person,
    Shelter
)
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

import pdb

from pets_seed import get_seed_class
from pets_script import PetApp

class ExpectedPet(object):
    "expected helper for creating and verifying pets"

    def __init__(self, **kwargs):
        "save keyword args as values for the pet"
        self.values = {}
        for k,v in kwargs.items():
            self.values[k] = v
     
    def get_args(self):
        "return a list of args as the app expects them"
        args = []
        for k,v in self.values.items():
            args.append( "%s:%s" % (k,v) )
        return args

    def verify(self, pet):
        "verify a pet object matches our starting values"
        for attr, expected_val in self.values.items():
            # for relations, we match on the name attribute
            if attr in ['breed','species','shelter']:
                assert getattr( getattr(pet, attr), 'name') == expected_val, (
                    "pet.%s should be %s is %s" % 
                    (attr, getattr(pet,attr), expected_val ) )
            else:    
                assert getattr(pet, attr) == expected_val, (
                    "pet.%s should be %s is %s" % 
                    (attr, getattr(pet,attr), expected_val ) )


class DBTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        "setup engine and session maker, runs once for suite"
        # this should come from an environment variable
        cls.db_url = "postgresql:///pets"
        cls.engine = create_engine(cls.db_url, echo=False)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        # create separate DB sessions for seeding and confirming
        self.init_tables(self.engine)
        self.seed = self.Session()
        self.confirm = self.Session()
        #self.clean_db(self.seed)

    def clean_db(self, session):
        "delete everything from the database without dropping tables"
        # delete from the pet_person table using SQLAlchemy expression language
        # guaranteed to catch any orphans in the many-to-many table
        conn = self.engine.connect()
        conn.execute( pet_person_table.delete() )
        # now delete everything else using the ORM
        for model in (Person, Pet, Shelter, Breed, Species):
            session.query(model).delete()
        session.commit()

    def init_tables(self, engine):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def seed_db(self, session):
        # fill our database up with starting content
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=tabby)
        session.add_all( [cat, dog, persian, tabby] )
        session.commit()

    def seed_from(self, seed_class):
        self.seed.add_all( seed_class._get_items() )
        self.seed.commit()

    def tearDown(self):
        # close our sessions
        self.seed.close()
        self.confirm.close()


class TestPets(DBTestSuite):

    def test_seed_examp(self):
        "test_seed_examp - example of seeding and verifying"
        seed_class = get_seed_class()
        # inherit from our seed class to add a species for this test only
        class SeedData(seed_class):
            parrot = Species(name="Parrot")
        self.seed_from( SeedData )
        num_species = self.seed.query(Species).count()

        # SUT execution will go here

        # now we verify postconditions with the confirmation session
        post_num_species = self.confirm.query(Species).count()
        self.assertEqual( num_species, post_num_species, 
            "species count should match" )
    
    def test_app_session(self):
        "test_app_session - instantiating PetApp should give us app.dbs session"
        try:
            app = PetApp(self.db_url)
            # verify the app has a session and that it works
            # try a query to make sure it works
            assert app._dbs.query(Pet).count() == 0, (
                "querying with app.dbs for pets count should give us a 0" )
        finally:
            app.clean_up()

    def test_get_pets_adopted(self):
        "test_get_pets_adopted - get_pets filtering on adopted attribute"
        # seed our database with the seed class
        self.seed_from( get_seed_class() )
        # use the seed session to  find out how many pets are adopted, 
        # this will keep working even if we change our seed class later
        expected_pet_count = self.seed.query(Pet).filter_by(adopted=True).count()
        
        # instantiate the app
        try:
            app = PetApp(self.db_url)
            # calling get_pets with this dict should give us two pets
            filter_dict = {'adopted':True}
            pets = app._get_pets( filter_dict )
            actual_pet_count = len(pets)
            
            self.assertEqual( expected_pet_count, actual_pet_count,
                "should get %i pets, got %i" % (expected_pet_count, actual_pet_count) )
            # verify the pets are adopted
            for pet in pets:
                self.assertEqual( pet.adopted, True, "pet should be adopted")
        finally:
            app.clean_up()


    def test_save_pet_breed_no_shelter(self):
        "test_save_pet_no_breed_no_shelter - save a new pet from dict"
        self.seed_from( get_seed_class() )
        pre_pet_count = self.seed.query(Pet).count()
       
        try:
            app = PetApp(self.db_url)
            # get the poodle breed
            # NOTE: we use the *app* session here, because we want to
            # to simulate what happens *in* the app
            app_poodle = app._dbs.query(Breed).filter_by(name="Poodle").first()
            new_pet_fields = dict(name='Fido', age=10, adopted=True, 
                dead=False, breed=app_poodle)
            # test the method that saveas a pet from a valid field dict
            app._save_pet( new_pet_fields )

            # VERIFY: get our new pet from the db
            new_pet = self.confirm.query(Pet).filter_by(name='Fido').first()
            # verify that our new pet has the same breed id
            # NOTE: we used the breed id as objects from different sessions
            # are *not* automatically equal
            self.assertEqual( new_pet.breed.id, app_poodle.id, "breed id should "
                "be %i is %i" % (new_pet.breed.id, app_poodle.id) )
        finally:
            app.clean_up()


    def test_create_pet_no_breed_no_shelter(self):
        "test_create_pet_no_breed_no_shelter - create a simple pet with no breed"
        self.seed_from( get_seed_class() )
        pre_pet_count = self.seed.query(Pet).count()
       
        try:
            # SUT execution
            app = PetApp(self.db_url)
            new_pet_args = ['name:Rex', 'age:10', 'adopted:0', 'dead:0']
            # call the top level method that should persist a new pet to the db
            app.add_pet( new_pet_args)

            # VERIFICATION verify we have 1 new pet in the DB
            post_pet_count = self.confirm.query(Pet).count()
            self.assertEqual(post_pet_count, pre_pet_count + 1, "pet cound should "
                "now be %i, is %i" % (pre_pet_count+1, post_pet_count) )
       
            # verify our pet's values are correct
            # get the newest pet from the DB:
            new_pet = self.confirm.query(Pet).filter_by(name='Rex').first()
            expected_vals = dict(name='Rex', age=10, adopted=False, dead=False)
            for key, expected in expected_vals.items():
                self.assertEqual( getattr(new_pet, key), expected_vals[key],
                    "%s should match, is: %s expected: %s" % (key,
                    getattr(new_pet, key), expected_vals[key]) )
        finally:
            app.clean_up()

    
    def test_pet_expected_match(self):
        "test_pet_expected_match - test the PetExpected class"
        expected = ExpectedPet( name="Newby", age=12, adopted=False, dead=False )
        newby = Pet(name='Newby', age=12, adopted=False, dead=False)
        expected.verify(newby)
    
    def test_pet_expected_no_match(self):
        "test_pet_expected_no_match - test the PetExpected class"
        expected = ExpectedPet( name="Newby", age=12, adopted=False, dead=False )
        newby = Pet(name='Wrong Name', age=12, adopted=False, dead=False)
        try:
            expected.verify(newby)
            assert False, "expected should have raised exception"
        except AssertionError:
            # what we want
            pass

 
    def test_add_pet_name_primitives(self):
        "test_add_pet_name_primitives - top level add a pet with only primitives"
        self.seed_from( get_seed_class() )
        
        # figure out how many pets should there be after we create one
        expected_pet_count = self.seed.query(Pet).count() + 1
       
        # create our expected, use it to hold the values we'll use
        expected = ExpectedPet( name="Newby", age=12, adopted=False, dead=False )

        try:
            # execute SUT
            app = PetApp( self.db_url )
            output = app.add_pet( expected.get_args() )
            
            # verify the returned output contains what we expect
            assert "New pet created. Name: Newby" in output, ( 
                "output should be success msg, was: %s" % output )
            
            # assert we have exactly 1 new pet in the database
            actual_pet_count = self.confirm.query(Pet).count()
            self.assertEqual( expected_pet_count, actual_pet_count, 
                "should be %i pets, is %i" % (expected_pet_count, actual_pet_count) )
            
            # get the most recently created pet from the database and verify 
            new_pet = self.confirm.query(Pet).order_by( desc(Pet.id) ).first() 
            # our expected's verify method will check all the values for us
            expected.verify(new_pet)
        
        finally:
            app.clean_up()
     
    def test_add_pet_name_existing_shelter(self):
        " test_add_pet_name_existing_shelter- top level add a pet an existing shelter"
        self.seed_from( get_seed_class() )
        
        # figure out how many pets should there be after we create one
        expected_pet_count = self.seed.query(Pet).count() + 1
      
        # get a shelter from the seed 
        shelter = self.seed.query(Shelter).first()

        # create our expected, use it to hold the values we'll use
        expected = ExpectedPet( name="Newby", age=12, adopted=False, dead=False,
            shelter=shelter.name)

        try:
            # execute SUT
            app = PetApp( self.db_url )
            output = app.add_pet( expected.get_args() )
            
            # verify the returned output contains what we expect
            assert "New pet created. Name: Newby" in output, ( 
                "output should be success msg, was: %s" % output )
            
            # assert we have exactly 1 new pet in the database
            actual_pet_count = self.confirm.query(Pet).count()
            self.assertEqual( expected_pet_count, actual_pet_count, 
                "should be %i pets, is %i" % (expected_pet_count, actual_pet_count) )
            
            # get the most recently created pet from the database and verify 
            new_pet = self.confirm.query(Pet).order_by( desc(Pet.id) ).first() 
            # our expected's verify method will check all the values for us
            expected.verify(new_pet)
        
        finally:
            app.clean_up()
 
    def test_add_pet_name_new_shelter(self):
        "test_add_pet_name_new_shelter - top level add a pet with new shelter"
        self.seed_from( get_seed_class() )
        
        # figure out how many pets should there be after we create one
        expected_pet_count = self.seed.query(Pet).count() + 1
        expected_shelter_count = self.seed.query(Shelter).count() + 1
       
        # create our expected, use it to hold the values we'll use
        expected = ExpectedPet( name="Newby", age=12, adopted=False, dead=False,
            shelter='SPCANEW')

        try:
            # execute SUT
            app = PetApp( self.db_url )
            output = app.add_pet( expected.get_args() )
            
            # verify the returned output contains what we expect
            assert "New pet created. Name: Newby" in output, ( 
                "output should be success msg, was: %s" % output )
            
            # assert we have exactly 1 new pet in the database
            actual_pet_count = self.confirm.query(Pet).count()
            self.assertEqual( expected_pet_count, actual_pet_count, 
                "should be %i pets, is %i" % (expected_pet_count, actual_pet_count) )
            # assert we have exactly 1 new shelter in the database
            actual_shelter_count = self.confirm.query(Shelter).count()
            self.assertEqual( expected_shelter_count, actual_shelter_count, 
                "should be %i shelters, is %i" % (expected_shelter_count, actual_shelter_count) )
            
            # get the most recently created pet from the database and verify 
            new_pet = self.confirm.query(Pet).order_by( desc(Pet.id) ).first() 
            # our expected's verify method will check all the values for us
            expected.verify(new_pet)
        
            # get the most recently created shelter from the database and verify 
            new_shelter = self.confirm.query(Shelter).order_by( desc(Shelter.id) ).first() 
            # assert the name is correct
            self.assertEqual(new_shelter.name, "SPCANEW", 
              "shelter name should be SPCANEW is %s" % new_shelter.name)


        finally:
            app.clean_up()
     


