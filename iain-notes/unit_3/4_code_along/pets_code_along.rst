Pet Project Code Along
======================

Deliverables
------------
First let's review the deliverables and think about what this might mean
for our high level architecture and the steps we need to take.

- The application is a command line app to search for pets or add
  a pet to our pet database from a terminal
- Command line arguments will be a field list in this format: 
     name:Ginger breed:labrador_retreiver age:10 species:dog 
- Searching for a pet will print out a list of pets matching the search terms
- The -a or -add flag will mean we create a pet instead of searching
- When creating a new pet, values for breed, species and shelter
  should check for existing matching entries and use them if present,
  or create new ones if none exist.
- The model should be stored in a separate file and imported
- The application should be created as an object that
  gets instantiated and then used from our __main__ function

To start with, let's think about what we know immediately:

- We need to create a new file with all the model definitions, which
  will be imported from our main script file 
- We need to parse command line arguments. We can use argparse.
- Our main file will contain an Application class that gets
  instantiated and used in the __main__ method.

We can see that this means we have three broad divisions
that ought to be decoupled from each other: our model, our
application classs, and our main script.

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
- Take a look at your database in the psql terminal and try inserting some data.
- If your model file is correct, you should get the same
  database table structures whether you create your database
  using the 'pets.sql' file or your model's main method.
- Open a python session. Import from your model. Make
  sure imports are working fine.


Application File
----------------

Thinking about our testing and design principles, we realize
we can limit the use of arparse to only the __main__ method.
If we parse our args there and then pass our parsed arguments
into the app class, our app class could be usuable in a different context;
it just needs to get the field argument strings somehow. We could
import the entire app class from something else and use it:
perhaps it might be used with an alternate user interface
such as a GUI or web form. This is a "Good Thing" for 
testing as it means our tests can also import the app class without
having to emulate arparse calls. This is a *decoupling* of two
of our broad components: the application, and the command line interface.
A good guideline is that anytime we can easily isolate dependencies,
such as on argparse, to limited components of our application, 
we should do so.

Ok, now we now that we'll have our main script get command line arguments,
and that it will instantiate an application class. We could pass the 
command line args into the app constructor, but that's not going
to make it as easy to test as if we keep the methods of the application
class more specific. The constructor should *make* the class, and
then we can have some public methods that the script will call on
the class. Sometimes we call the app to search and sometimes to add pets.
So let's decide now that we'll have two public top level methods for
our app class, one for searching and one for adding, and those
will take as arguments a list of strings of our fields such as this::

    ['name:titch', 'age:10', 'species:cat' ...]

Now what do we mean by "public methods"? Public means that the methods
or attributes are meant to be called or used by external code, as in code 
that is not contained in a method of our class. Conversely, private means
that *only* code within our class should use the method or attribute.
Now in actuality, Python is very permissive in this regard, the language
will not enforce privacy the way Java or C++ does. In those languages
we can mark a method as private or public, and the compiler will enforce
these rules: you really can't break them, you'll get an error.
In Python, the interpreter can't enforce privacy; privacy is just a 
convention, or a hint to other programmers of our intent. 
Nontheless, naming our methods and attributes to distinguish between these
two is useful when designing a larger project. 
It means that if we have other components that only
interface with our class through public methods, then we know which
parts of class we can redo at anytime without affecting *any*
code outside of class, so long as the interfaces of our
public methods are maintained: IE they must accept the same arguments
and return the same values.  This principle is called encapsulation, and
is an important part of good object oriented design.

In Python, a commonly used convention is to 
preface our internal private methods and attributes with an underscore to indicate
that they should be "considered private". This gives us a nice visual 
indicator that if we are calling or using those from outside our class, something
is wrong. So we'll name our top level methods "search" and "add_pet".

Another good convention that goes in hand with this is to give our
public methods detailed doc strings indicating what they expect
in arguments ("preconditions") and what they will return or do 
("postconditions"). This describes our public interface, and once
we've got that figured out, we should nail it down and keep it still.
This process is sometimes called "freezing the API". Once that has
happened, we know external components can use our object freely
without fear that we might break the application somehow in an internal
change. 

Now let's think about our app's lifecycle. At the end of the script,
we terminate and the class will be automatically deleted from
memory when our script ends. Are we safe
in assuming one lifecycle of the app should only be using one
database? Sounds like it. Is the database integral to the app?
Yes, it can't do anything without it. So that sounds like
a good case for sending the db_url to the app constructor as an
argument. We also know that we'll need an SQLAlchemy session object for working
with the database, so we can have our constructor create the session.
And we know that we definitely don't want external code, sometimes called "client code"
to be reading or writing to this session object, so we'll name the
session self._dbs as a hint that it should be private.
Our constructor then has a specific job: get the
object ready for interacting with the database. We'll make sure
that's detailed in our docstring so users of our class now
how our object works.

"Users of our class"? Another good rule of thumb when designing
decoupled systems is to pretend you're working in a team. A good
design will allow different people to work on different compoments
without everyone having to understand everything about every component.
If they know the interface expectations of our class, they should be
able to use it. Imagining this, we can see why documention for
the public interfaces is the most important.

So we know we need:
- An application class: PetApp
- A constructor that takes a db_url and creates self._dbs
- A public top level search method taking a field list.
- A public top level add method taking a field list.

Our deliverables also say that we'll be printing output.
We could print directly from the pet app, however, it's going to
be easier to use our PetApp class in our test suite if we're trying 
to verify return values (returning a string) instead of side effects
(printing to the console), so let's have our top level
'search' and 'add' method return strings and we'll print them
from the main method. This also makes sense because if wanted 
to give our PetApp a GUI or web interface, we wouldn't want it 
to print. 

So now we have a good idea of the interface of our public methods:
they will take string arguments of some kind, and return string 
output. Let's stub those out know and give them some docstrings.
One point about the constructor: despite it's name being prefaced
with two underscores, it's really part of our public interface,
so it should get a detailed docstring too. 
We'll make the components and get
them to fake that they do the right thing just to get going::

    # TODO: set up the logger

    class PetApp(object):

        def __init__(self, db_url):
            """
            Create and initialize the PetApp object, creates
            an sqlalchemy engine and session for the database.
            Initializes self._dbs, the SQLAlchemy session.
            param db_url: a db connection string
            """
            log.info("PetApp.__init__() db_url: %s" % db_url)
            # TODO: create SQLA session as self._dbs
            self._dbs = None 

        # public search method
        def search(self, field_list):
            """
            Search for pets from a list of search terms.
            
            param field_list: a list of strings such as:
                ['name:titchy','breed:tabby']
            returns: string output from the search with pet details.
            """
            log.info("PetApp.search() field_list: %s" % field_list)
            return "Search output"

        # public add pet method
        def add_pet(self, field_list):
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
            log.info("PetApp.add() field_list: %s" % field_list)
            return "Adding Pet output"


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

Exercise 2
----------
- Update the __main__ method to use argparse to get the field arg
  list from the command line
- Using argparse, have __main__ chose the operation: We'll call 
  the 'add' method if the user uses either '-a' or '--add' at the 
  command line, or default to 'search'
- Update __main__ so that the db_url can be either taken from
  command line flag ('-d') or read from an environment variable
  called 'DB_URL'. (Either is fine).

At this point, we've established a starting point for our
public interfaces, and we can run our script and get our sample
output. In essence, we've created an internal Application Programming
Interface, or API, for our class, as we've determined how the rest of our
application should interact with it. Now we need to make the internals
fulfill the promises in their interfaces.

Connecting to the database
--------------------------
Now before trying to make the app do exactly what we want with
the database, let's just try getting it to do *something*. 
This is a case where it's fine
to write some throw away code that just gets us somewhere so we know
we're accessing the model ok. Let's use our search method and give
it a temporary task of listing all the cats in our database. 
It's not going to be doing the *right* thing, but it's going to be
doing something that is inline with our interface, IE it does
a search and returns a string of pets found. This kind of interative
building process is a really good way to
break down a complex task, and the act of fulfilling our interface
requirements (if incompletely) will help us find out quickly if
we've made a poor decision with regards to our interface. 

We've already established that the SQLAlchemy session will be 
created by the constructor, so let's get that ready. We
don't need to make the engine and Session maker attributes
of the class as we're pretty sure that other methods will
only interact with the database through the session object.
So we'll keep those as local variables for now (encapsulation again!)::

    def __init__(self, db_url):
        """
        Create and initialize the PetApp object, creates
        an sqlalchemy engine and session for the database.
        Initializes self._dbs, the SQLAlchemy session.
        param db_url: a db connection string
        """
        log.info("PetApp.__init__() db_url: %s" % db_url)
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        self._dbs = Session()

We'll also add a method to close down the session when we're done. 
In normal use this would happen automatically when the script terminates
as the session will be garbage collected (BEN do they know what this means),
but we want to design our application for extensibility and it's quite
likely that in testing we'll have extra instances hanging about, so we'll
clean up after ourselves for good measure. We're going to make the 
clean up method public because it's also possible that the app might get
used in a context where an exception is caught by the calling code and
the session should be closed even when an exception is raised. For example, 
the calling code might need to do something like this ::

    app = PetApp(db_url)
    try:
        app.search(args)
    finally:
        app.clean_up()

In the above example, no matter what happens in our app, the session will
get closed by the clean_up method. It's ok if this means that clean_up
gets called twice though, SQLAlchemy doesn't mind if we try to close a 
session that is already closed. So let's add that now. ::

    def clean_up(self):
        "close our session"
        self._dbs.close()

In our terminal application, we're imagining that the app object is 
thrown away after use, but we generally want to plan for easy extensibility
when we can. So what will happen if we've cleaned up, and we want to 
run another search on the same app object? As it turns out, SQLAlchemy 
is smart about this, closing a session doesn't delete the session, it just
flushes it out, and prepares it for the next round of use, so we're ok 
on that front. You can test this out by dropping into pdb after a clean_up
call and using the session again. 

Now that our session is ready for use, we'll make our search method
do something::

    def search(self, field_args):
        """
        Search for pets from a list of search terms.
        
        param field_list: a list of strings such as:
            ['name:titchy','breed:tabby']
        returns: string output from the search with pet details.
        """
        
        # query for our pets
        pets = self._dbs.query(Pet).all()
        # some temporary string formatting
        output = "Pets: " + ", ".join( [pet.name for pet in pets] )

        # we're done with our session so close it
        self.clean_up()
        return output


Now to get the above working, we'll need to import the model:

Exercise 3 - Hooking up SQLAlchemy
----------------------------------
- Add imports to the top of our script, we need to import all
  our model class from pets_model.py
- Get it going to the point that a call to our script for searching
  spits out our list of Pets, and test this in the terminal
- Create a temporary version of the add_pet method too that adds
  a pet with hardcoded values to the database, ignoring the relations.

Now we can test this out in the terminal, and get a string back
with a list of pets, hooray! At this point, we've got all our high
level parts created and talking to each other. 
If this works, we can probably settle on our frozen API. 
This is a good first step in app design. 
That said, when coming up with the broad breakdown into components, you'll
frequently get it wrong the first time, so it's nice to be doing this
when we have only small stub content in our methods.

Assuming we're happy with evereything, from here on, we want to 
keep things working and incrementally move from our temporary features 
over to code that does the real work.

It would be a good plan at this point to write some tests. However,
testing applications that connect to databases is pretty complex so
we're going defer covering that to the next assignment, and continue
building our application.

Implementing the Features
-------------------------
Now it's time to think a bit more about how we're going to get the
app doing the right thing. Once we know the mile high view, we can
often feel overwhelmed by the next step as there is so much to do.
A good practise when you feel that way is to just make a list of things
you *know* you need to figure out, and tackle some in isolation. 
Well, we know we'll need to:

- Turn those weird input strings into meaningful values,
  probably some kind of dictionary.
- Search for Pets.
- Search for existing breeds, shelters, or species, creating
  them if need be.
- Save a Pet somehow, maybe from a dictionary of values.
- Create our final formatted string output from a list of Pets.
- Create our final formatted string output after creating a Pet.

Some of those sound easy, and some sound hard. If we have good ideas 
already for solving the hard ones, we could dive into those, resolving our detail helpers
as we go. If we don't, we can let them simmer in our brains while
we knock off some of the easy ones as helper methods. 
Let's do that so we can get some unit tests going too. 
We'll know our helpers are well designed if
they can be tested with free standing unit tests *before* we 
do the tricky stuff.


String Output
-------------
Well, we need to creat formatted output for both adding a pet
and searching for pets. Here we're going to take advantage
of what is called in the world of dynamic languages "duck typing".
Duck typing comes from the expression "if it walks like a duck and
quacks like a duck, it is a duck". Because Python is un-typed, we
can assign any type of value to any variable. In typed languages 
such as C++ or Java, if a variable is meant to store integers,
it can only store integers (without trickery...). If Python were
"strongly typed" we could only test our output routines by passing
in actual lists of Pet objects. Because Python uses duck typing, 
all we need to do is pass in objects that "quack like a duck". Or 
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
'age', or 'adopted', these fake pet objects will work fine for
our unit tests.  Of course if we don't set an attribute on our mocks that our
method needs, we're going to get an error. So if we want
some attributes to return None values, we should either 
beef up the mock's constructor to set default values or make
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
attribute look up, things get trickier. A good rule of thumb
is to always be extra careful anytime your client code is
using a variable with more than one level of attribute look up,
IE more than one dot! One approach is
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
from the database to test it.::

    def _search_output(self, pets):
        """
        create the string output from a list of pets
        param pets: a list of pet objects to display
        """
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        return output

Now we can create ourselves a unit test file, which will
import our application class from our main file. In the unit
test class we can use mocks to emulate the pets::

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


More problems! How can we instantiate our app in a test when it wants to connect
to the database right off in the constructor? This is a big question and 
there are several ways to tackle this.

We could just leave things as they are and decide that all instantiations
need a valid database.  This is reasonable, but means it's harder to write
*true* unit tests.  Everything will wind up also being an *integration* or
*functional* test, because we'll need to integrate with a database. This
is going to slow down our tests and make them harder to write though.

Another approach is to compose our app differently
so that it's easier to instantiate partial versions of the app. For
example, we could wrap up all the database connection innards in their
own special object and have this new object get passed into the app at
startup time, so that in our test scenario we could pass a fake version
of this hypothetical object in to get up and running.  For big complex
projects, this can be a good way to go, and an entire area of programming 
called Dependency Injection is devoted to this sort of solution. The
"dependency" is wrapped up in an isolated component, and then "injected"
in to the app class. Our app would then depend on more 
discreet component objects and some master system would create them and 
lash everything together. However, for our little app, this will be overkill,
we would wind up with a lot more classes and files, and we'd need to 
use a dependency injection master system, so we won't do that.

A third approach is to alter our app so that if we try to instantiate
it without a db_url, it gets created but skips connecting to the database,
allowing us to at least test methods that don't require the database.
The problem with this is that we wind up with code in our app who's
*only purpose* is to behave differently for testing. Sometimes this
is necessary and justifies itself, but we want to avoid that situation
if at all possible. A good design should allow us to test the app
and have it run *exactly* as it will in production.

A final option, and the one we're going to use, is to change our method
so that it doesn't even need a reference to self, and can thus
be tested *without* ever instantiating our application class.

Static and Class Methods:
-------------------------
We can do this by making this output method a *static method*.
It will be a plain-old-function, without any expectation of getting
a pet app as the first argument. If we
aren't writing to self or reading from self (self being the app object) then 
we don't even need self in there. All we need to do to make this a
static method is add the @staticmethod decorator and remove self from
the paramater list ::

    @staticmethod
    def _search_output(pets):
        # NOTE: no self as the first argument!
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        return output

It's now basically just a normal function that happens to have it's 
code inside our class. This is sometimes referred to as using the class
for "namespacing", because our method is named "Pet.search_output" instead
of "search_output".  Now if our method needed to use other helper methods
from the class, we could alternately make it a **class method**, where we 
replace self with a reference to the class ::

    @classmethod
    def _search_output(cls, pets):
        # NOTE: self has been replaced with cls
        output = "Pets found:\n"
        for pet in pets:
            output += "%s, age: %s breed: %s species %s" % 
                (pet.name, pet.age, pet.breed.name, pet.breed.species.name)
        
        # cls holds the value PetApp as a class
        # if we wanted to use other classmethod helpers, we can get
        # at them using cls.whatever_helper()
        return output

In both cases, they can now be called from the class name::

    # call our method, get output
    output = PetApp._search_output(mock_pets)

One of the neat features of class and static methods is that they can still
be called from instances, so if you aren't using a reference to self in
your method body, there's really no penalty for using a static or class method::

    # we can still do this even though search_output is a class method 
    pet_app = PetApp(db_url)
    pet_app._search_output(pets)

In application code, seeing "Pet._search_output" would be a strong warning
that we've used a private method somewhere we shouldn't. After all,
internal code ought to be able to use this as "self._search_output". The
exception to this is testing: in a test scenario we'll frequently find
ourselves calling code in contexts other than the intent of the design,
so this is ok.

Exercise 4
----------
- Create a new file for our unit tests, with a unittest Test Case class
- Write static or class methods that return formatted string output for
  the results of a pet search or a new pet addition. The new pet version
  can take the new pet as an argument. Both will return strings.
- Write unit tests for these methods using mock pet objects.
- Write another helper, 'fields_to_dict' that takes in the list of arguments as strings
  from arg parse and returns a dictionary. 
  IE we'll receive a list like
  ['name:titchy', 'age:10'] and get {'name':'titchy', 'age':10 }
  This can also be a static method.
- Write some unit tests for your 'fields_to_dict' helper too.

Note: all the helpers are only intended for internal use and so
should be prefaced with our privacy hinting underscore.

Searching
---------
Ok, let's take stock, we've got our app. It connects to the database ok.
It saves a pet. We can return output. We get args. We can convert args.
We're ready for the heavy lifting. Let's break it down into steps and 
start by ignoring the relationships: no breed, shelter, or species.

First let's flesh out our top level search method with what we have so far,
we'll use our newly created _fields_to_dict helper method and we'll
call our output method at the end to format the strings::

    def search(self, field_args):
        """
        Search for pets from a list of search terms.
        
        param field_list: a list of strings such as:
            ['name:titchy','breed:tabby']
        returns: string output from the search with pet details.
        """
        # get a dictionary of search terms with our helper
        filter_dict = self._fields_to_dict(field_args)
        # TODO get pets somehow
        pets = self._get_pets(filter_dict)  # <-- doesn't exist yet!
        # return string output
        output = self._search_output(pets)
        
        self.clean_up()
        return pets

So we need a way to get pets from a filter dict. We'll call this private
method '_get_pets'. It just needs to execute search queries. If we're ignoring
the relations, this should be pretty straightforward. We'll make a base
query and then filter it with our search terms. As this is a private
method with a small specific task, we don't need to make such a detailed
doc string.::

    def _get_pets(self, filter_dict):
        "return a list of Pet objects from a filter dict"
       
        # make our base query
        query = self._dbs.query(Pet)
        # TODO: deal with breed, species, shelter

        # filter on fields (name, age, dead, adopted)    
        for field_name, field_value in filter_dict.items():
            if hasattr(Pet, field_name):
                query = query.filter( getattr(Pet, field_name) == field_value)

        # now execute our query
        pets = query.all()
        return pets
 
We can try this out, and for a simple search we should now have enough of
an app for the whole thing to work!

Now to deal with our relations. Let's try it first with just shelter::

    def _get_pets(self, filter_dict):
        "return a list of Pet objects for a filter dict"
        
        # make our base query
        query = self._dbs.query(Pet)
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
then query. We'll make another helper, "_normalize_name", using the 'title' method
of the Python string object. Seems like another good candidate for a static method::

    @staticmethod
    def _normalize_name(name):
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
- Add a unittest for our _normalize_name helper
- Add a filter on breed section to our get_pets method, making
  sure to normalize the breed name before we filter.
- Add a filter clause for species. Test it out with the terminal.


Adding A Pet
------------
Now we can move on to adding the pet. Looking at this closely, we
can see the tricky business is going to be checking for the relations
and creating new ones if we need to. So let's defer that and just
get a Pet saving without any of those complications. We'll just
hardcode our choices for those for now.

We can re-use our _fields_to_dict helper, as we'll still need 
to those values. So for our top level method, we'll have something like
this ::

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
        
        # get our random temp relation values for breed and shelter
        # we don't need species as it's a relation of Breed
        fields['breed'] = self._dbs.query(Breed).first()       
        fields['shelter'] = self._dbs.query(Shelter).first()       
        
        new_pet = Pet()
        for attr,value in fields.items():
            if hasattr(Pet, attr):
                setattr(new_pet, attr, value)
        self._dbs.add( new_pet )
        self._dbs.commit()
        
        output = self._add_output(pet)
        
        self.clean_up()
        return output


Looking at the above, we see that the actual database 
interaction is limited to the second last block of code,
so let's put those in a helper called "_save_pet". As
this uses the database session, this is not a suitable
candidate for a static or class method::


    def add_pet(self, field_args):
        """
        top level method to add a new pet to the db
        - creates breed, species, & shelter if needed
        - returns string output with success message and pet name
        - NB: does not yet have error handling
        """
        print "Adding pet to database: %s" % field_args
        # convert fields to a dict of key/val pairs 
        fields = self._fields_to_dict(field_args)
        
        # get our random temp relation values for breed and shelter
        # we don't need species as it's a relation of Breed
        fields['breed'] = self._dbs.query(Breed).first()       
        fields['shelter'] = self._dbs.query(Shelter).first()       
       
        # call our new helper to save the pet
        new_pet = self._save_pet( fields )
        
        output = self._add_output(pet)
        
        self.clean_up()
        return output


    def save_pet(self, fields):
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
            
So now we're saving pets and we can start to think about the relations.
Let's think about the logic, and use shelter for our example. A good
practice for something tricky is write it out in pseudocode as 
comments first: ::

    def add_pet(self, field_args):
        ...
        # if there is a shelter in fields
            # check for shelter in database
            # if found
                # use this shelter
            # else
                # create a new shelter
                # use this new shelter
        

Doing this will really help us see how our branching is looking and
means we'll be more likely to lay it out properly. Next we should
ask how we're using shelter when we create the pet. We can either
use an instantiated shelter object and write it to pet.shelter or 
we can use a shelter id and write it to pet.shelter_id. Looking at
our pseudocode, we see we're going to have to query for shelter objects
anyway. And looking at our pet saving helper, we see we are writing
key value pairs from the fields dict to the pet object, so it seems
like getting a shelter object and writing to pet.shelter will be easiest.
It also will mean that if we're making a new shelter, we won't have 
to run an intermediate database commit just to get the shelter id.

So now we start turning our pseudocode into real code ::

TODO: check that first is the right method to use here:

    def add_pet(self, field_args):
        ...
        fields = self._fields_to_dict(field_args)
        
        # if there is a shelter in fields
        if 'shelter' in fields:     
            # check for shelter in database
            shelter = self._dbs.query(Shelter).filter(
              Shelter.name==fields['shelter'] ).first()
            # if found
            if shelter:    
                # use this shelter
                fields['shelter'] = shelter
            # else
            else:
                # create a new shelter using the name given
                shelter = Shelter( name=fields['shelter'] )
                # use this new shelter
                fields['shelter'] = shelter
        
        # continue

You can see how well this works for keeping track of what needs doing.
Now we delete our comments ::

        if 'shelter' in fields:     
            shelter = self._dbs.query(Shelter).filter(
                Shelter.name==fields['shelter'] ).first()
            if shelter:    
                fields['shelter'] = shelter
            else:
                shelter = Shelter( name=fields['shelter'] )
                fields['shelter'] = shelter
        
Let's test it out at the terminal and make sure it works. Once we've done
so, we can refactor this code. Refactoring means we rearrange and redo the
implementation of code that already works. A good practice for hard problems
is to get an initial version and a test passing, then refactor once you have
a test so that you know that your refactored version is working. 
We'll move this block of code into its 
own helper method as our indent level is getting pretty deep::

   def add_pet(self, field_args):
        fields = self._fields_to_dict(field_args)
       
        # use a python ternary expression to set fields['shelter'] 
        # to either a shelter object or None
        fields['shelter'] = self._get_shelter( fields['shelter'] ) if \
            'shelter' in fields else None
        
        pet = self._save_pet( fields )
        output = self._add_output(pet)
        
        self.clean_up()
        return output


    def get_shelter(self, shelter_arg):
        """
        convert a shelter string to an instantiated shelter object
        - optionally creates a new shelter in the db if need be
        """
        # check for existing shelter by this name
        shelter = self._dbs.query(Shelter).filter(
            Shelter.name==shelter_name).first()
        # if none found, create new shelter
        if not shelter:
            shelter = Shelter(name=shelter_name)
            self._dbs.add(shelter)
        return shelter

Now we have a helper with a very specific job, and when it comes time
to write database tests, it will be easier to test. And our add_pet
method is nice and succint again.

We'll repeat this process for Species and Breed. Note that there 
is some additional complexity with breed because we can't make a
breed without a species. So we'll only create new breeds if we 
have a valid species argument, and we'll be passing a species reference
into our breed helper.

Exercise 6
----------
- Go through the above to make sure your clear on how it all works.
- Repeat this process for breed and species, then compare to our version
  once you've got your own.

Our version of this is below. It's not ideal because the species
value really just gets thrown out if we don't also have breed because
our pets only have a reference to species *through* breed. But short
of retooling our database to deal with this, it will suffice::


    def add_pet(self, field_args):
        """
        top level method to add a new pet to the db
        - creates breed, species, & shelter if needed
        - returns string output with success message and pet name
        - NB: does not yet have error handling
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

    def get_species(self, species_arg):
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


    def get_breed(self, breed_arg, species=None):
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


    def get_shelter(self, shelter_arg):
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


Conclusion
----------
Our pet script is now complete. We can add pets or search for pets,
and we are able to create new a new breed, species, and shelter if
required. In the next assignment we'll go into how we will write
automated tests for our application.
