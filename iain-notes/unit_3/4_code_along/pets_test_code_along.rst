Pet Project Database Tests Code Along
=====================================

In this assignment we'll be covering how to write automated tests for our
database application, bearing in mind our test principles that we've already
discussed. 

The main concern for database application testing is that we want to make sure
that we are able to start each test with a specific database precondition,
execute the test, and then verify the database postcondition. And we need to do this
in such a manner that tests can run in any order or in isolation, and that writing
new tests is relatively painless. This means that each test must do some kind
of automated database preparation. The process of filling a database with sample
data for a test is often called "database seeding" and the files or data used
for doing this are often called "text fixtures" or "seed data". 

There are a number of options for test fixtures. We can use SQL files,
or files of JSON data, or even Python itself. SQLAlchemy lends itself very
well to writing fixtures directly in Python, which will give us a great deal
of flexibility in setting up our tests, so that's what we'll be using in this
assignment. 

The unittest framework for Python allows us to write our test suites as classes,
with special methods that will execute before and after the entire suite, and
before and after each test. We'll take advantage of this by writing a base class
that takes care of our database housekeeping for us in these setup and teardown
methods, and then our actual test classes can inherit from this utility base class.

We'll also take advantage of SQLAlchemy's session management for preparing
and verifying our test database. Because a session object keeps its own
identity map, we can use more than one session at a time, and know that objects
from one will not collide or interfere with objects from another. 

The mile high overview is that we want our test suite to do the following:

* Create a database engine and sessions that we can use for test fixtures
  for test verification.
* Put our database into a clean starting state before each test.
* Help us verify database post conditions.

We'll create two database sessions, one for seeding the database (fixture data)
and the other for confirming after application execution that the database
is in the correct state. To make our tests more readable, we'll call one of 
these sessions "seed" and the other "confirm".

So let's start creating our test classes. 

Connecting to the database
--------------------------
We need to create an engine and a sessionmaker to use SQLAlchemy sessions,
but the engine and sessionmaker don't need to be recreated for each test,
so we'll put them in the unittest **setUpClass** method, a class method
that is executed before any tests in a suite: ::

    class DBTestSuite(unittest.TestCase):
    
        @classmethod
        def setUpClass(cls):
            "setup engine and session maker, runs once for suite"
   
            cls.db_url = "postgresql:///pets"
            cls.engine = create_engine(cls.db_url, echo=False)
            cls.Session = sessionmaker(bind=cls.engine)

Reflecting on our previous discusson of test principles, we remember 
that it should be trivial
to change the database being used for our tests. So we'll use an 
**Enviroment Variable** to hold our database connection string. This way
the tester can export the correct value for the database connection string
to the local environment prior to running the tests and we won't have it
hardcoded into a bunch of files.

(XXX: BEN, do we need to point them at an ENV variable tutorial?)

While we build our test class, we'll need a sample test suite to see
if it's working. So let's add a derived class with a dummy test.
We can use this dummy test as we go to find out if we have errors
in our base class. ::

    class TestExample(DBTestSuite):
        
        def test_example(self):
            "a test that should pass"
            assert True

Now we can run our test file from the command line with unittest in verbose
mode and see our test executing::

    $ python -m unittest -v test_utils

Exercise 1:
-----------
- Create a new file, "test_utils.py".
- Add the necessary imports for unittest and sqlalchemy.
- Create your base test class from the example above
- Add a derived test suite with a dummy test.
- Get your test passing.
- Now alter your base class to get the database connection string
  from an enviroment variable.
- Export your environment variable from a terminal, execute your
  test suite, and get it passing again. 


Preparing the Database
----------------------
Our test class now connects to the database, once per execution of the
whole suite. Our next task is to prepare  for interacting
with the database on a per test basis. We'll use the unittest setUp and 
tearDown methods to create (and then close) sessions for each test, and
we'll create two different session objects and name them so that it's clear
which is for seeding the database and which is for confirming our database
post conditions. And we'll create a method for wiping our database for
each test pass. ::

    class DBTestSuite(unittest.TestCase):
        
        # setUpClass omitted

        def setUp(self):
            # create separate DB sessions for seeding and confirming
            self.seed = self.Session()
            self.confirm = self.Session()
            self.clean_db(self.seed)
 
Our clean_db method can work two different ways. We can either drop
and recreate all our tables, or just empty them. Dropping the tables
is easy enough because we can use the metadata object to do so ::

        def init_tables(self):
            # assuming we've imported Base from our model
            Base.metadata.drop_all( self.engine )
            Base.metadata.create_all( self.engine )

One wrinkle about the above when working with PostgreSQL is that PostgreSQL
is very particular about dropping tables when a connection is open, so we
need to make sure there are no active sessions when we issue our drop and create
statements. This requires us to make the call *before*
we create our sessions, and to make sure that after every test all sessions
(including the app's session) are definitely closed. So our setUp
method would be ::

        def setUp(self):
            # create separate DB sessions for seeding and confirming
            self.init_tables(self.seed)
            self.seed = self.Session()
            self.confirm = self.Session()

And in every test we'll make sure that the app's clean_up method gets called
no matter what, by using a try/finally block ::

        def test_example(self):
            # instantiate the app and force cleanup
            try:
                app = PetApp(self.db_url)
                # more test stuff will go here 
            finally:
                # this will now execute whether or not we got an exception
                app.clean_up()

For a big database, dropping and creating all the tables can get pretty slow.
Our other option is to delete everything from all the tables that we
want to seed on each test. This requires more code in the cleaning routine,
but executes much faster. In our case, we'll need to use SQLALchemy's expression
language to delete from the pet_person join table as it won't get automatically emptied
if we delete with our ORM. If we had set our mappers differently this might
not be necessary. It's best when writing a routine to wipe your database tables
that you check in the terminal to make sure it's really doing what you want. 
This version uses the a session, so we'd need to call it after creating our
sessions, and we'd pass the seed session in as the first parameter. ::

        def clean_db(self, session):
            "delete everything from the tables"
            # delete from the pet_person table using SQLAlchemy expression language
            # guaranteed to catch any orphans in the many-to-many table
            conn = self.engine.connect()
            conn.execute( pet_person_table.delete() )
            # now delete everything else using the ORM
            for model in (Person, Pet, Shelter, Breed, Species):
                session.query(model).delete()
            session.commit()

Some people prefer to use the tearDown method to close sessions, drop tables,
or delete objects. While this make semantic sense, one side effect of this is that 
you can't run one test in isolation and then check on the database post-condition
using psql in the terminal, as after each test everything's gone. Both approaches
are fine, but if you are having a hard time getting a particularly tricky test 
working, being able to look at the database post test can be very helpful, so
we'll use that approach here.


Exercise 2
----------
- Add the setUp routine and helpers for dropping and creating tables and
  for deleting all objects in the database
- Create *two* sample tests that instantiate your app and clean up afterwards
  using a try/finally block. We need two as with only one we can't be sure
  that the clean up between tests is working properly. 
- Get your tests passing, and try out both methods of database clean up.


Seeding With Sample Data
------------------------
To run tests that simulate the application properly, we're going to need 
data in our database prior to the test. This process is sometimes called
"seeding the database". While there are a number of approaches to this, the
we'll use SQLAlchemy's ORM to create seed data in Python. This makes
it very easy for us to alter our seed data (and thus our database precondition)
right in the test code.

For a very small initial database, we can just make a helper method to drop 
in some data with our seed session: ::

    def seed_db(self, session):
        # fill our database up with starting content
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=tabby)
        session.add_all( [cat, dog, persian, tabby] )
        session.commit()

We would then call this in our test using the seeding session ::

    def test_example(self):
        # seed the database
        self.seed_db( self.seed )
        # now instantiate the app and test
        try:
            app = PetApp( self.db_url ) 
            # test stuff here
        finally:
            app.clean_up()

We can come up with a set of starter items that are good for most
of our tests, and add or delete from that for individual tests that
need specific unique preconditions.  We can even alter our helper so
we can pass in a list of extra database entries for these special cases. ::

    # Note the addition of items=[]
    def seed_db(self, session, items=[]):
        # fill our database up with starting content
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=tabby)
        session.add_all( [cat, dog, persian, tabby] )
        # add the extra items
        if items:
            session.add_all( items )
        session.commit()

    def test_example(self):
        # create some items for just this test
        seed_items = [
            Pet(name="Fifi),
            Person(name="Iain")
        ]
        # seed the database
        self.seed_db( self.seed, seed_items )
        
        # now instantiate the app and test
        try:
            app = PetApp( self.db_url ) 
            # test stuff here
        finally:
            app.clean_up()

Exercise 3
----------
- Add a database seeding helper with some sample data.
- Alter your example tests to call this seed method.
- Run your suite with at least two dummy tests. Take a look
  at the database in the terminal afterwards and make sure all
  is as you'd expect.


Reusable Seed Classes
---------------------
This works well for small databases, and we could of course also make 
a helper specific to one test (or several) or create all our seed objects
in the test.  However, once our database needs get bigger, this becomes 
pretty cumbersome. 
An elegant solution to this is to use the dynamic nature of Python's class
statement to make a seed class that we can inherit from for non-standard cases.
You'll frequently see this kind of use (or abuse as some say) of the class statement
in Python frameworks. We'll create our seed objects as class-level attributes
of a seed class ::

    class SeedData(object):
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=tabby)
        titchy = Cat(name='Titchy', breed=tabby)
    
What we need to remember here is that the code in a class runs when that class
is defined, so our database items will get created when the Python interpreter
hits this class statement. If we just put this class statement at the top
of our file, we will create them once, globally. But if we put this statement
inside a function, and *return* the class as an object, we'll have a function we 
can call anytime to instantiate a bundle of new database seed items::

    def get_seed_class():

        # class definition statement will run when get_seed_class is called
        class SeedData(object):
            cat = Species(name="Cat")
            dog = Species(name="Dog")
            persian = Breed(name="Persian", species=cat)
            tabby = Breed(name="Tabby", species=tabby)
            titchy = Cat(name='Titchy', breed=tabby)
       
        # return our dynamically created class, with all its items
        return SeedData    
    
Now each time we call get_seed_data, we get a new class with a new set of 
seed items. If we add a helper to our SeedData class that returns a list
of all internal items, we can use this as a very handle bundler. We'll do this
by making a base SeedClass class with a helper that returns all class 
attributes that don't start with an underscore. ::

    class SeedClass(object):
       
        @classmethod
        def _get_items(cls):
            "return all non-private attributes (our items) of the class"
            items = []
            for attr in dir(cls):
                if attr[0] != "_":
                    items.append( getattr(cls, attr) )
            return items


    def get_seed_class():
        
        class SeedData(SeedClass):
            cat = Species(name="Cat")
            dog = Species(name="Dog")
            persian = Breed(name="Persian", species=cat)
            tabby = Breed(name="Tabby", species=tabby)
            titchy = Cat(name='Titchy', breed=tabby)
        
        return SeedData    

We can then use this in our test very easily. ::

    def test_example(self):
        self.seed.all_all( get_seed_class()._get_items() )
        self.seed.commit()
        # continue test

Mind you, that first line is not terribly readable, so let's wrap
it up in a helper to keep our tests easier to follow and type. ::

    def seed_from(self, seed_class):
        "get items from a seed class and commit them"
        self.seed.add_all( seed_class._get_items() )
        self.seed.commit()

    def text_example(self):
        self.seed_from( get_seed_class() )
        # continue test

Now the real reason seed classes are so convenient is because we can now alter 
our seed data in our individual tests by *inheriting* from our dynamically
created class. ::

    def test_example(self):
        # make a slight variant to our seed class
        
        # get the base class
        seed_class = get_seed_class()

        # use the base class to derive a new class
        class SeedData( seed_class ):
            # get rid of titcy, we don't want him for this test
            titchy = None
            # but add a new pet. Note that we can refer to other seed items
            ginger = Pet(name='Ginger', breed=seed_class.dog)

        # now use our new seed class
        self.seed_from( SeedData )
        # continue on with test

A further advantage of this is that we can easily get values from our
seed class if we want to use them for verification as well, they're 
still available to us:

   def test_example(self):
        # make a slight variant to our seed class
        seed_class = get_seed_class()
        class SeedData( seed_class ):
            # get rid of titcy, we don't want him for this test
            titchy = None
            # but add a new pet, with ability to refer to other seed items
            ginger = Pet(name='Ginger', breed=seed_class.dog)
        self.seed_from( SeedData )
        # continue on with test
   
        # an assertion using a value from our seed class
        self.assertEqual( some_var, seed_class.titchy.name, 
            "Name should match titchy's name")

Now we can make one or two large seed data classes that give us
our normal database precondition for most tests and keep those in a 
separate file that we import and inherit from when we need specific
preconditions.

Exercise 4
----------
- Create a new file, "pets_seed.py".
- Put in a base seed class (wrapped in a callable) and create a sample
  seed data class with entries for Breed, Species, Pet, Person, and Shelter.
- Edit your base test suite class to add helpers for working with the
  seed class.
- Alter your first sample test to import this class and seed the database. 
- Alter your second test to make a new derived seed class with some differences.
- Get both tests passing, and check out the results in your database.


Testing the Application
-----------------------
At this point all our tests are getting a fresh database and we can start
testing our application. As the application's database session is created
in the app's constructor, we'll start by instantiating the application
with the database connection string for our test database. Then we
can call methods on it, verifying the return values and
database postconditions. Let's start by testing one of the application
methods that returns values. The _get_pets method accepts a dictionary
of filter terms and returns pets that match. For comprehensive testing,
we'll want to make sure that our tests cover various versions of the 
filter dict, including filtering on relationships. We'll use a seed class,
and for now let's assume our seed class contains two adopted pets. We'll
give our test a descriptive name and a docstring that clearly indicates 
what we're expecting. ::

    def test_get_pets_adopted(self):
        "test_get_pets_adopted - get_pets filtering on adopted attribute"
        # seed our database with the seed class
        self.seed_from( get_seed_class() )
        # use the seed session to  find out how many pets are adopted, 
        expected_pet_count = self.seed.query(Pet).filter_by(adopted=True).count()
        
        # instantiate the app
        try:
            app = PetApp(self.db_url)
            # calling get_pets with this dict should give us two pets
            filter_dict = {'adopted':True}
            pets = app._get_pets( filter_dict )
            actual_pet_count = len(pets)
            
            self.assertEqual( expected_pet_count, actual_pet_count,
                "should get %i pets, got %i" % 
                (expected_pet_count, actual_pet_count) ) 
            # verify the pets are adopted
            for pet in pets:
                self.assertEqual( pet.adopted, True, "pet should be adopted")
        finally:
            app.clean_up()

Let's look at the above in a bit more detail. Once we've seeded the database,
we'll query it with the seed session to find the number of adopted pets. 
We're querying for this value rather than taking it from our seed class because
this way our test will continue to work when we expand our seed class as we
write new tests. Whenever possible, we want to keep hardcoded values out
of the tests so that our tests aren't brittle. We use the seed session for this query,
and we store the results in a variable that is clearly named for its role.
Tests act as a good source of documentation for how the
app is supposed to work, so naming variables such that it's immediately obvious
what's going on is worth the extra typing.

When we instantiate the app, we wrap our testing part in the try/finally block
so that no matter what happens, the app's clean_up method will get called
to close the application's database session.

Our assertion includes a string that will get printed if the assertion fails,
and we have both the expected and actual values in there. For simple cases
this is optional, but for tests that aren't working the message is very helpful.
We limit our assertions to one conceptual truth: we are getting back two adopted
pets.

One tricky part of testing is figuring out how much coverage we need. In this
case, we probably don't need to write separate tests for all the possible
items in the filter dict, but we should write some new ones for each relationship
at least. Another good rule of thumb is to have tests written for different
counts of items, making sure you have a test for: none, one, more than one.

Exercise 5
----------
- Add the test for _get_pets to your own test file and get this working.
- Add variants of this that filter on: breed name, species name, shelter name.
- Add a test with more than one item in the filter dict.
- Add a test with zero items in the filter dict. Does it do what you expect?
- Add a test for the top level search method. This one will have different
  input format and will have to look for values in the output string to 
  verify success.

Verifying Post Conditions & Expecteds
-------------------------------------
Finally we need to write some tests for creating pets. This has the additional
complexity of a change to our database. We'll start with our simplest possible
case, a pet with only a name. As with the searching cases, we'll write tests
for the saving method and also for the top level add pet method. To illustrate
the difference, this time we'll start by testing the top level method first.

For this test, we need to have a dictionary of starting values, and we'll want
to verify that our newly created pet matches the starting values. As we're going
to have to write a handful of tests to verify our add pet method is working, we'll
create a helper class that can be used both to hold pet values and verify in one
line of code that the whole pet matches.  This kind of helper class is sometimes
called an "Expected". 

When we create a pet, we're going to have starting values that are strings
for breed, shelter, and species. Verifying on those will be unique to the way
those attributes work, so we'll have special match cases for those that knows
to check the name field and consider it a match if the name matches. ::

    class ExpectedPet(object):
        def __init__(self, **kwargs):
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



Of course we'll need to test our expected class too. We'll create two small tests
to verify it does its job correctly ::

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
            assert False, "expected should have raised an exception"
        except AssertionError:
            # getting here constitutes success
            pass

This may seem like a lot of work, but in a large app, the overhead of created
an expected class is warranted by the speed up it gives us in writing tests. We
want to do whatever we can to make sure tests are easy to read and write. Furthermore,
the infrastructure for an Expected class doesn't change too much from one project
to another, so you'll be able to re-use previous expected classes when you're making
them.

Now that we've got our handy helper, let's build our add pet test. In this test
we're going to need to verify a few different things: we get a returned string that 
says we're successful, we create one and only one pet in the database, and
this pet has the correct values. To do this we'll count the number of pets
in the precondition database. (Again we won't just use the value from our seed
class in case this value changes.) Then we'll execute the SUT, getting back a string
value that we can check for success. And finally, we'll use our "confirm" session to
get the most recent pet addition in the database and verify it against our expected
to make sure it's correct. ::

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
     

And we're passing! Another useful practice when writing complex functional
tests like these is to verify that your test is doing the right thing by deliberately
making it fail first. It's quite possible in these sorts of tests to have two
errors that cancel each other out, such as the expected misbehaving during the verify
method. Try changing a couple of values and getting it to fail predictably as well.
If you're not sure whether this sort of thing is happening, dropping into the debugger
in the middle of your test and checking the Python objects against your database
is a good practise.

Now we need to think about our more complex cases for adding a pet. Let's start with the
simplest one: we have a shelter argument, and it matches one of our existing shelters.
Our expected's verify method should "just work" on this because it knows to assert on 
the name field of Shelter, and the argument passed in from the command line is just the
shelter's name. So this should be a very simple variant of the previous test: ::

    def test_add_pet_name_existing_shelter(self):
        " test_add_pet_name_existing_shelter- top level add a pet an existing shelter"
        self.seed_from( get_seed_class() )
        
        # figure out how many pets should there be after we create one
        expected_pet_count = self.seed.query(Pet).count() + 1
      
        # get a shelter from the seed data 
        shelter = self.seed.query(Shelter).first()

        # create our expected, use it to hold the values we'll use
        # note we're using shelter.name because the app is expecting
        # the shelter argument to be a string of the name
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
            # including the new shelter attribute
            expected.verify(new_pet)
        
        finally:
            app.clean_up()
 
Continuing on our possible scenarios, we have the case of a shelter argument
with a new shelter.  
In this case, success means that a new pet and a new shelter were created in the database.
So we'll copy our first add_pet test and add in shelter verification. ::

    def test_add_pet_name_new_shelter(self):
        "test_add_pet_name_new_shelter - top level add a pet with new shelter"
        self.seed_from( get_seed_class() )
        
        # figure out how many pets and shelters there should be after test
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
    
This is a pretty comprehensive test of the entire life of our app class,
and it's not going to be difficult to write variants of it.

Exercise 6
----------
- Add new tests for the add_pet method for the following scenarios:
  - an existing breed is specified
  - a new breed is specified, with an existing species name
  - a new breed is specified, with a new species name
  - a new species is specified, with no breed name

- Look through your app and see whether there are any methods missing tests. 
  Add some tests for them if so.

Further Reading:
----------------
Much of the material in this section was taken from the excellent book,
"XUnit Test Patterns", by Gerard Meszaros. You can read it online as well as
http://www.xunitpatterns.com

