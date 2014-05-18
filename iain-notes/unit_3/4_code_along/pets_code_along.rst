Pet Project Code Along
======================

Deliverables
------------
First let's review the deliverables and think about what this might mean
for high level architecture and steps to achieve.

- The application is a command line app to search for pets or add
  a pet to our pet database from a terminal
- Command line arugments will be a field list in this format: 
     name:Ginger breed:labrador_retreiver age:10 species:dog 
- Search output prints out a list of pets matching the search terms
- The -a or -add flag will instead creates a new pet
- When creating a new pet, values for breed, species and shelter
  should check of existing matching entires and use them,
  or create new ones if none exist.
- The model should be stored in a separate file and imported
- The application should be created as an object that
  gets instantiated and then used from __main__

To start with, let's think about what we know immediately:

- We need to a file with all the model definitions and it will
  be imported from our main file
- We need to parse command line arguments. We can use argparse
  for that. 
- Our main file will contain an Application class that gets
  instantiated and used in the __main__ method.

We can see that this means we have three broad divisions
that ought to be decoupled: model, main script, app class.

With regards to the model file, we can put the method for
initializing the database (dropping and creating tables)
in there. Let's add a main method to our model file so
that if it's used as the main app (IE $ python pets_model.py )
we create the tables. Of course this could be disastrous 
if done by accident, so let's have a confirmation step in there
too. 

Here's my initial main method for the model file::

    if __name__ == "__main__":
        # if run this model file as the main script
        # it will initialize our database

        db_url = 'sqlite:///pets_code_along.db'
        # create an engine
        engine = create_engine(db_url, echo=True)
        # drop all tables and recreate
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        print "Database initialized, exiting."

That's workable, but it has the db_url hardcoded in
and doesn't have any confirmation step.

Exercise 1 - Model File
-----------------------
- Move all your model definitions into one file. Use
  the 'pets.sql' file as your reference for what this 
  model should look like.
- Update the sample main method to ask the user for
  confirmation before tables are dropped.
- Add the ability to pass in a db_url as a command line argument
- Use the model file to create your new database.
  Take a look at it in the terminal and try inserting some data.
- If your model file is correct, you should get the same
  database table structures whether you create your database
  using the 'pets.sql' file or your model.
- Open a python session. Import from your model. Make
  sure imports are working fine.


Application File
----------------

Thinking about our testing and design principles, we realize
we can limit the use of arparse to only the __main__ method.
If we parse our args there and then pass them into the app 
class, our app class could be usuable in a different context,
it just needs to get the field argument strings. We could
import the entire app class from something else and use it,
perhaps it might be used with an alternate user interface
like a GUI or web form. This is a Good Thing already for 
testing as it means our tests can also import the app without
having to emulate arparse calls.

Sometimes we call the app to search and sometimes to add pets.
So let's decide now that we'll have two top level methods for
our app class, one for searching and one for adding, and those
will take as arguments a list of strings of our fields:

    ['name:titch', 'age:10', 'species:cat' ...]

Let's think about our app's lifecycle. At the end of the script,
we terminate and the class is garbage collected. Are we safe
in assuming one lifecycle of the app should only be using one
database? Sounds like it. Is the database integral to the app?
Yes, it can't do anything without it. So that sounds like
a good case for sending the db_url to the app constructor as an
argument.

So we know we need:
- An application class: PetApp
- A constructor that takes a db_url
- A top level search method taking a field list.
- A top level add method taking a field list.

Now our deliverables also say that we'll be printing output.
We could print directly from the pet app, and my first version
did just that. However, it's going to be easier to use our 
PetApp in our test suite if we're trying to verify return
values instead of side effects, so let's have our top level
'search' and 'add' method *return* strings and we'll print them
from the main method. This also makes sense because if wanted 
to give our PetApp a GUI or web interface, we wouldn't want it 
to print.

Let's stub those out know. We'll make the components and get
them to fake that they do the right thing just to get going::

    # TODO: set up the logger

    class PetApp(object):

        def __init__(self, db_url):
            log.info("PetApp.__init__() db_url: %s" % db_url)

        def search(self, field_list):
            log.info("PetApp.search() field_list: %s" % field_list)
            return "Search output goes here"

        def add(self, field_list):
            log.info("PetApp.add() field_list: %s" % field_list)
            return "Adding Pet output goes here"


    if __name__=="__main__":

        # TODO get this from command line args
        field_list = ['name:titchy', 'age:10', 'species:cat']
        
        # TODO get this from command line args
        operation = 'search' 
        # operation = 'add'

        # TODO get this from a command line arg or an ENV variable
        db_url = "postgresql:///pets"

        # instantiate an instance of our PetApp  
        pet_app = PetApp(db_url=db_url)
    
        # call the pet app to either add a pet or search for pets
        if operation = 'add':
            output = pet_app.add_pet(fields_list)
            print output
        else:
            output = pet_app.search(fields_list)
            print output

Ok, that's a good start. We can run our script, and we get our sample
output. 

Exercise 2
----------
- Update the __main__ method to use argparse to get the field arg
  list from the command line
- Using argparse, have __main__ chose the operation: We'll call 
  the 'add' method if the user uses either '-a' or '--add' at the 
  command line, or default to 'search'
- Update __main__ so that the db_url can be either taken from
  command line flag ('-d') or read from an enviroment variable
  called 'DB_URL'. (Either is fine).


Connecting to the database
--------------------------
Ok, we have a skeleton that works pretty well. Now before trying
to make the app do exactly what we want with the database, let's just
try getting it to do *something*. This is a case where it's fine
to write some throw away content that just gets us somewhere so we know
we're accessing the model ok. Let's use our search method and give
it a temporary task of listing all the cats in our database. We 
know we'll be connecting to the database somewhere, so let's decide
that we'll have a member variable on our app called 'dbs' for 
database session, and it will be an instantiated working SQLAlchemy
session::

    def search(self, field_list):
        log.info("PetApp.search() field_list: %s" % field_list)
        pets = self.dbs.query(Pet).all()
        output = "Pets: " + ", ".join( [pet.name for pet in pets] )
        return output

Ok, this won't work right now, and that's fine. We know we need
to create an engine, create a sessionmaker and get a session, 
so let's put all that in our constructor ::

    def __init__(self, db_url):
        log.info("PetApp.__init__() db_url: %s" % db_url)
        # TODO: create engine, sessionmaker
        self.session = Session()


Exercise 3 - Hooking up SQLAlchemy
----------------------------------
- Add imports to the top of our script, we need to import all
  our model class from pets_model.py
- Flesh out our constructor to create the engine and sessionmaker
- Get it going to the point that a call to our script for searching
  spits out our list of Pets
- Add throw-away content to the 'add' method to create a random
  pet. Get that working.


At this point, we've got all our parts talking to each other. This
is a good first step in app design. You will frequently get it wrong the
first time and it's a lot more productive to be redoing the component
break down when they only have tiny stub content in them.


Now it's time to think a bit more about how we're going to get the
app doing the right thing. Once we know the mile high view, we can
often feel overwhelmed by the next step as there is so much to do.
A good practise when you feel that way is to just make a list of things
you *know* you need to figure out, and tackle some in isolation. 
Well, we know we'll need to:

- Turn those weird input strings into meaningful values,
  probably some kind of dictionary
- Save a Pet somehow, maybe from a dictionary of values.
- Create our final formatted string output from a list of Pets
- Search for Pets.
- Search for existing breeds, shelters, or species, creating
  them if need be.

The last two sound hard. If we have good ideas for solving them
right now, we could dive into those, resolving our detail helpers
as we go. If we don't, we can let them simmer in our brains while
we knock off some of the helpers. Let's do that so we can get some
unit tests going too. We'll know our helpers are well designed if
they can be tested *before* we do the tricky stuff.


Output
------
Ok, we need to creat formatted output for both adding a pet
and searching for pets. Here we're going to take advantage
of what is called in the world of dynamic languages "duck typing".
Duck typing comes from the expression "if it walks like a duck and
quacks like a duck, it is a duck". Because Python is un-typed, we
can assign any type of value to any variable. In typed languages 
such as C++ or Java, if a variable is mean to store integers,
it can only store integers (without trickery...) If Python were
"strongly typed" we could only test our output routines by passing
in actual lists of Pet objects. Because Python uses duck typing, 
all we need to do is pass in objects that quack like a duck. Or 
rather, have values for the attributes we are *expecting* to be
there for Pet objects. We don't *really* need
to pass it pet objects, just objects that satisfy
our *interface requirements*. In our case, as we're just 
printing out values that we get from pet.name, pet.age, pet.adopted,
pet.shelter, pet.breed, and pet.species, that's all our objects need
to satisfy. 

Testing with Mock Objects
-------------------------
For our tests, we can make fake pet objects with those values
available, and in Python, this is really easy to do using dynamic keyword
arguments::

    class Mock(object):
        "a generic mock object"
        def __init__(self, **kwargs):
            for attr,val in kwargs.items():
                setattr(self, attr,val)

Now we can make a list of fake Pets using this Mock class::

    pets = [ 
        Mock(name="Titchy", age=17, adopted=1),
        Mock(name="Ginger", age=1, adopted=1),
        Mock(name="Kizmet", age=9, adopted=1)
    ]

If all we do with our pets inside our method is ask for 'name',
'age', or 'adopted', these fake pet objects will work fine.
Of course if we don't set an attribute on our mocks that our
method needs, we're going to get an error. So if we want
some attributes to return None values, we should either 
beef up the mocks constructor to set default values or make
sure we set them when we make fake pets ::

    class MockPet(Object):
        "a mock pet, has defaults for all pet attributes"
        def __init__(self, **kwargs):
            for attr in ['name','age','adopted','dead',
                'breed', 'species', 'shelter']:
                setattr(self, attr, kwargs.get(attr, None) )    

This version of our mock object has default values for
every pet attribute we might use regardless of whether 
we initialize them. To figure out if this is sufficient,
we need to figure out what we're going to ask for. Uh-oh,
what if we ask for *pet.breed.name*? Whenever we have nested
attribute look up, things get trickier. One approach is
to improve our mocks so this will work by nesting mocks::

    # assuming both the Mock class and MockPet class are defined
    # enable reads for pet.breed.name, pet.breed.species.name
    mock_pets = [
        MockPet( name='Titchy', age=17, adopted=True, dead=True,
            breed=Mock( name='Tabby', species=Mock(name='Cat') ),
            shelter=Mock( name='BCSPCA )
        ),
        MockPet( name='Ginger', age=1, adopted=True, dead=False,
            breed=Mock( name='Labradoodle', species=Mock(name='Dog') ),
            shelter=Mock( name='BCSPCA )
        ) ]

With the above version of our mocks, even if our output routine
asks for **pet.breed.species.name**, we're going to be fine.

Now we can write a method for our pet searching and an 
accompanying unit test, without having to get real pets
from the database ::

    def search_output(self, pets):
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        return output

    # assuming our Mock classes have been defined somewhere
    # and imported prior to this test exectuting

    def test_pet_search_output(self):
        mock_pets = [
            MockPet( name='Titchy', age=17, adopted=True, dead=True,
                breed=Mock( name='Tabby', species=Mock(name='Cat') ),
                shelter=Mock( name='BCSPCA' ) ),
            MockPet( name='Ginger', age=1, adopted=True, dead=False,
                breed=Mock( name='Labradoodle', species=Mock(name='Dog') ),
                shelter=Mock( name='BCSPCA' ) )
      
        # now instantiate our app and use the pets


More problems! How can we instantiate our app when it wants to connect
to the database right off? This is a big question and there are
several ways to tackle this.

We could just decide that all instantiations
need a valid database. This is reasonable, but means it's harder
to write *true* unit tests. Everything will wind up also being an 
*integration* or *functional* test, because we'll need to integrate
with a database. 

Another approach is to compose our app differently
so that it's easier to instantiate partial versions of the app. For
example, we could wrap up all the database connection inards in their
own object and have this thing passed into the app at startup time,
so that we could pass a fake version of this hypothetical object in
to get up and running.  For big complex projects, this can be a good way
to go, and an entire area of programming called Dependency Injection 
is devoted to this sort of solution. Our app would then depend on more 
discreet component objects and some master system would create them and 
lash everything together. However, for our little app, this will be overkill.

A third approach is to alter our app so that if we try to instantiate
it without a db_url, it gets created but skips connecting to the database,
allowing us to at least test methods that don't require the database.
The problem with this is that we wind up with code in our app who's
*only purpose* is to behave differently for testing. Sometimes this
is necessary and justifies itself, but we want to avoid that situation
if at all possible.

A final option, and the one we're going to use, is to change our method
so that it doesn't even need a reference to self.

Static and Class Methods:
-------------------------
We can do this by making this output method a *static method*.
It will be a plain-old-function, without any expectation of getting
a pet app as the first argument. If we
aren't writing to self or reading from self (self being the app) then 
we don't even need self in there. All we need to do to make this a
static method is add the @staticmethod decorator and remove self from
the paramater list ::

    @staticmethod
    def search_output(pets):
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        return output

It's now basically just a normal function that happens to live inside
our class. If our method needed to use other helper methods from the class,
we could alternately make it a class method, where we replace self
with a reference to the class ::

    @classmethod
    def search_output(cls, pets):
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        
        # cls holds the value PetApp as a class
        # if we wanted to use other classmethod helpers, we can get
        # at them using cls.whatever_helper()
        return output

In both cases, they can now be called from the class name *as well* as from
an instance variable ::

    # call our method, get output
    output = PetApp.search_output(mock_pets)

One of the neat features of class and static methods is that they can still
be called from instances, so if you aren't using a reference to self in
your method body, there's really no penalty for using a static or class method::

    # we can still do this in normal use:
    pet_app = PetApp(db_url)
    pet_app.search_output(pets)

Exercise 4
----------
- Create a new file for our unit tests, with a unittest Test Case class
- Write static or class methods that return formatted string output for
  the results of a pet search or a new pet addition. The new pet version
  can take the new pet as an argument. Both will return strings.
- Write unit tests for these methods using mock pet objects.
- Write a new helper, 'fields_to_dict' that takes in the list of arguments as strings
  from arg parse and returns a dictionary. IE we'll receive a list like
  ['name:titchy', 'age:10'] and get {'name':'titchy', 'age':10 }


Searching
---------
Ok, let's take stock, we've got our app. It connects to the database ok.
It saves a pet. We can return output. We get args. We can convert args.
We're ready for the heavy lifting. Let's break it down into steps and 
start by ignoring the relationships: no breed, shelter, or species.

First let's flesh out our top level search method with what we have so far::

    def search(self, field_args):
        """
        top level method to search for pets from input args"
        returns a formatted string list of pets to the terminal
        """
        # get a dictionary of search terms with our helper
        filter_dict = self.fields_to_dict(field_args)
        # TODO get pets somehow
        pets = self.get_pets(filter_dict)  # <-- doesn't exist yet!
        # return string output
        output = self.search_output(pets)
        return pets

So we need a way to get pets from a filter dict. We'll call this method 'get_pets'.
Get pets really just needs execute search queries. If we're ignoring
the relations, this should be pretty straightforward. We'll make a base
query and then filter it with our search terms::

    def get_pets(self, filter_dict):
        "return a list of Pet objects for a filter dict"
        
        query = self.dbs.query(Pet)
        # TODO: deal with breed, species, shelter

        # other fields (name, age, dead, adopted)    
        for field_name, field_value in filter_dict.items():
            if hasattr(Pet, field_name):
                query = query.filter( getattr(Pet, field_name) == field_value)

        # now execute our query
        pets = query.all()
        return pets
 
We can try this out, and for a simple search we should now have enough of
an app for the whole thing to work! We'll be dicussing how to setup automated
tests for this later as it's pretty involved so for now just test it out at the 
command line.

Now to deal with our relations. Let's try it first with just shelter::

    def get_pets(self, filter_dict):
        "return a list of Pet objects for a filter dict"
        
        query = self.dbs.query(Pet)
        # TODO: deal with breed, species, shelter

        # filter on shelter
        if 'shelter' in filter_dict:
            query = query.join(Shelter)
            # pop from filter dict so the value is gone from the dict
            query = query.filter(Shelter.name == filter_dict.pop('shelter') )

        # other fields (name, age, dead, adopted)    
        for field_name, field_value in filter_dict.items():
            if hasattr(Pet, field_name):
                query = query.filter( getattr(Pet, field_name) == field_value)

        # now execute our query
        pets = query.all()
        return pets

Testing this out, we're working again. We want to add Breed now. But what
if someone enters "poodle" and our table holds values for breed with the first
letter capitalized? We should normalize our input search term for breed and
then query. We'll make another helper, "normalize name", using the 'title' method
of the Python string object. Seems like another good candidate for a staticmethod::

    @staticmethod
    def normalize_name(name):
        "convert underscores to spaces and use title case"
        name = name.replace('_',' ').title()
        return name

Now we can filter on breed. What about species? Species will be a bit
trickier because Species is not an attribute of Pet, it's a relationship
on Breed. So we'll need to add another join::

    query = query.join(Breed).join(Species)

Other than that, it should be similar.

Exercise 5:
-----------
- Add a unittest for our normalize_name helper
- Add a filter on breed section to our get_pets method, making
  sure to normalize the breed name before we filter.
- Add a filter clause for species. Test it out with the terminal.


Adding A Pet
------------
Now we can move on to adding the pet. Looking at this closely, we
can see the tricky business is going to be checking for the relations
and creating new ones if we need to. So let's defer that and just
get a Pet working without any of those complications. We'll just
hardcode our choices for those in first to get it working.

We can re-use our fields_to_dict helper, as we'll still need 
to those values. So for our top level method, we'll have something like
this ::

    def add_pet(self, field_args):
        """
        top level method to add a new pet to the db
        - creates breed, species, & shelter if needed
        - returns string output with success message and pet name
        - NB: does not yet have error handling
        """
        print "Adding pet to database: %s" % field_args
        # convert fields to a dict of key/val pairs 
        fields = self.fields_to_dict(field_args)
        
        # get our random temp relation values for breed and shelter
        # we don't need species as it's a relation of Breed
        fields['breed'] = self.dbs.query(Breed).first()       
        fields['shelter'] = self.dbs.query(Shelter).first()       
        
        new_pet = Pet()
        for attr,value in fields.items():
            if hasattr(Pet, attr):
                setattr(new_pet, attr, value)
        self.dbs.add( new_pet )
        self.dbs.commit()
        
        output = self.output_new_pet(pet)
        return output
            
Looking at the above, we see that all the actual "talking to the database"
bits are in the second last block of code, so let's put those in a helper so we can
write smaller tests ::


    def add_pet(self, field_args):
        """
        top level method to add a new pet to the db
        - creates breed, species, & shelter if needed
        - returns string output with success message and pet name
        - NB: does not yet have error handling
        """
        print "Adding pet to database: %s" % field_args
        # convert fields to a dict of key/val pairs 
        fields = self.fields_to_dict(field_args)
        
        # get our random temp relation values for breed and shelter
        # we don't need species as it's a relation of Breed
        fields['breed'] = self.dbs.query(Breed).first()       
        fields['shelter'] = self.dbs.query(Shelter).first()       
       
        new_pet = self.save_pet( fields )
        
        output = self.output_new_pet(pet)
        return output


    def save_pet(self, fields):
        "persist a pet to the DB from a dict of values"
        new_pet = Pet()
        for attr,value in fields.items():
            if hasattr(Pet, attr):
                setattr(new_pet, attr, value)
        self.dbs.add( new_pet )
        self.dbs.commit()
        return new_pet 
            
So now we're saving pets and we can start to think about the relations.
Let's think about the logic, and use shelter for our example. A good
practice for something tricky is write it out in pseudocode as c
comments first ::

    def add_pet(self, field_args):
        # omitting doc strings here ...
        fields = self.fields_to_dict(field_args)
        
        # if there is a shelter in fields
            # check for shelter in database
            # if found
                # use this shelter
            # else
                # create a new shelter
                # use this new shelter
        
        # continue

Doing this will really help us see how our branching is looking and
means we'll be more likely to lay it out properly. Next we should
ask how we're using shelter when we create the pet. We can either
use an instantiated shelter object and write it to pet.shelter or 
we can use a shelter id and write it to pet.shelter. Looking at
our pseudocode, we see we're going to have to query for shelter objects
anyway. And looking at our pet saving helper, we see we are writing
key value pairs from the fields dict to the pet object, so it seems
like getting a shelter object and writing to pet.shelter will be easiest.
It also will mean that if we're making a new shelter, we won't have 
to run an intermediate database commit just to get the shelter id.

So now we start turning our pseudocode into real code ::

    def add_pet(self, field_args):
        # omitting doc strings here ...
        fields = self.fields_to_dict(field_args)
        
        # if there is a shelter in fields
        if 'shelter' in fields:     
            # check for shelter in database
            shelter = self.dbs.query(Shelter).filter(
              Shelter.name==fields['shelter'] ).first()
            # if found
            if shelter:    
                # use this shelter
                fields['shelter'] = shelter
            # else
            else:
                # create a new shelter
                shelter = Shelter( name=fields['shelter'] )
                # use this new shelter
                fields['shelter'] = shelter
        
        # continue

You can see how well this works for keeping track of what needs doing.
Now we delete our comments ::

        if 'shelter' in fields:     
            shelter = self.dbs.query(Shelter).filter(
                Shelter.name==fields['shelter'] ).first()
            if shelter:    
                fields['shelter'] = shelter
            else:
                shelter = Shelter( name=fields['shelter'] )
                fields['shelter'] = shelter
        
Let's test it out at the terminal and make sure it works. Once we've done
so, we can refactor this code. Refactoring means we rearrange and redo the
implementation of code that already works. A good practice for hard problems
is to get a test passing somehow, then refactor once you have a test so you 
now that you're refactor works. We'll move this block of code into its 
own helper method as our indent level is getting pretty deep::

   def add_pet(self, field_args):
        fields = self.fields_to_dict(field_args)
       
        # use a python ternary expression to set fields['shelter'] 
        # to either a shelter object or None
        fields['shelter'] = self.get_shelter( fields['shelter'] ) if \
            'shelter' in fields else None
        
        pet = self.save_pet( fields )
        output = self.output_new_pet(pet)
        return output

    def get_shelter(self, shelter_arg):
        """
        convert a shelter string to an instantiated shelter object
        - optionally creates a new shelter in the db if need be
        """
        # we use the shelter name as is, no normalizing
        shelter = self.dbs.query(Shelter).filter(
            Shelter.name==shelter_name).first()
        if not shelter:
            shelter = Shelter(name=shelter_name)
            self.dbs.add(shelter)
        return shelter



       
