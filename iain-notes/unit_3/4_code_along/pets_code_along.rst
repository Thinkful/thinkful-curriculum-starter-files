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
and searching for pets. This is place where we can take advantage
of what is called in the world of dynamic languages "duck typing".
Duck typing comes from the expression "if it walks like a duck and
quacks like a duck, it is a duck". Because Python is untyped, we
can assign anything to anywhere, pretty much. So if we make a helper
method that expects a list of pet objects, and all it does is
read our pet attributes from those objects, we don't *really* need
to pass it pet objects. We can pass it *anything* that satisfies
our *interface requirements*. If we want to print out the pet
name, age, adopted, and shelter, then we just need a list of objects
that return values for name, age, adopted, and shelter. This is
good use case for test-first development.



