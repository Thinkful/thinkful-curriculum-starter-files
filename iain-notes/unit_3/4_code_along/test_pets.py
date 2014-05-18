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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pdb

from pets_seed import get_seed_class
from pets_script import PetApp

class DBTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # runs once for the whole class, setup engine

        # this should come from an environment variable
        cls.db_url = "postgresql:///pets"
        cls.engine = create_engine(cls.db_url, echo=False)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        # create separate DB sessions for seeding and confirming
        self.seed = self.Session()
        self.confirm = self.Session()
        self.clean_db(self.seed)

    def clean_db(self, dbs):
        "delete everything from the database without dropping tables"
        # delete from the pet_person table using SQLAlchemy expression language
        # guaranteed to catch any orphans in the many-to-many table
        conn = self.engine.connect()
        conn.execute( pet_person_table.delete() )
        # now delete everything else using the ORM
        for model in (Person, Pet, Shelter, Breed, Species):
            dbs.query(model).delete()
        dbs.commit()

    def manual_seed_db(self, dbs):
        # fill our database up with starting content
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=tabby)
        dbs.add_all( [cat, dog, persian, tabby] )
        dbs.commit()

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
        app = PetApp(self.db_url)
        # verify we have a session and that it works
        # try a query to make sure it works
        assert app.dbs.query(Pet).count() == 0, (
            "querying with app.dbs for pets count should give us a 0" )


    def test_get_pets_adopted(self):
        "test_get_pets_adopted - get_pets filtering on simple attributes"
        # seed our database with the seed class
        self.seed_from( get_seed_class() )
        # use the seed session to  find out how many pets are adopted, 
        # this will keep working even if we change our seed class later
        num_adopted_pets = self.seed.query(Pet).filter_by(adopted=True).count()
        
        # instantiate the app
        app = PetApp(self.db_url)
        # calling get_pets with this dict should give us two pets
        filter_dict = {'adopted':True}
        pets = app.get_pets( filter_dict )
        num_pets = len(pets)
        
        self.assertEqual( num_pets, num_adopted_pets,
            "should get two pets, got %i" % num_pets)
        # verify the pets are adopted
        for pet in pets:
            self.assertEqual( pet.adopted, True, "pet should be adopted")

    def test_save_pet_breed_no_shelter(self):
        "test_save_pet_no_breed_no_shelter - save a new pet from dict"
        self.seed_from( get_seed_class() )
        pre_pet_count = self.seed.query(Pet).count()
       
        app = PetApp(self.db_url)
        # get the poodle breed
        # NOTE: we use the *app* session here, because we want to
        # to simulate what happens *in* the app
        app_poodle = app.dbs.query(Breed).filter_by(name="Poodle").first()
        new_pet_fields = dict(name='Fido', age=10, adopted=True, 
            dead=False, breed=app_poodle)
        # test the method that saveas a pet from a valid field dict
        app.save_pet( new_pet_fields )

        # VERIFY: get our new pet from the db
        new_pet = self.confirm.query(Pet).filter_by(name='Fido').first()
        # verify that our new pet has the same breed id
        # NOTE: we used the breed id as objects from different sessions
        # are *not* automatically equal
        self.assertEqual( new_pet.breed.id, app_poodle.id, "breed id should "
            "be %i is %i" % (new_pet.breed.id, app_poodle.id) )


    def test_create_pet_no_breed_no_shelter(self):
        "test_create_pet_no_breed_no_shelter - create a simple pet with no breed"
        self.seed_from( get_seed_class() )
        pre_pet_count = self.seed.query(Pet).count()
       
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

    # TODO for the student: make test methods that verify things are working
    # with new or existing breeds and new or existing shelters


    def test_thing(self):
        self.seed_from( get_seed_class() )
        pets = self.seed.query(Pet).all()
        app = PetApp(self.db_url)
        pdb.set_trace()
