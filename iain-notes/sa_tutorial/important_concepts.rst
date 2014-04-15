Important Concepts in SQLAlchemy
================================

SQLAlchemy is an advanced library and supports a number of different ways of working. It is
enormously flexible, and has been designed to ensure that one will not "outgrow" SQLAlchemy
as a problem becomes more complex. The cost of this flexibility is that SQLAlchemy
uses some programming concepts that are fairly advanced and not immediately obvious to a new user. 
Understanding SQLAlchemy is a lot easier if these **design patterns** are understood at the outset,
and if the role of the different components in play is clear.

Factory Functions
-----------------
SQLAlchemy uses factory functions to dynamically generate *classes*. In Python, a class is itsefl an object,
it is just a callable object that returns a new object when called. This means a class itself can be built
and returned by a function.  

A factory function that builds a class is often used in a situation where the components of the class depend on some 
information that is not available until *runtime*.  In SQLAlchemy we see factory functions 
used to build our data model base class and also to build the Session class. 

The main thing to beware of here is to watch your capitalization, these are classes and should begin 
with upper case letters. ::

    # import the declarative_base factory function
    from sqlalchemy.ext.declarative import declarative_base

    # dynamically build our base class
    Base = declarative_base()

    # use our base class
    class Pet(Base):
        ...etc...

Once the Base class has been built by the factory function, it is used as normal just as
if it had been imported.


Data Mapper & Declarative Base
------------------------------
SQLAlchemy uses a pattern called **Data Mapper** to persist objects. In the Data Mapper pattern, 
A data model is defined with regular Python classes, which we will refer to as our Domain Model
classes. A separate set of objects representing the database tables are also 
created and these are then **mapped** dynamically to our data model classes using SQLAlchemy's **mapper** function.
The Data Mapper pattern is very flexible because it doesn't make any assumptions about how our Python
classes map to our tables, if the database grows and we need to change our  table structure or even how many 
tables are mapped to each class we can easily do so. 

In **Classical Mapping**, these three components are declared separately.
Older versions of SQLAlchemy *only* supported classical mapping, so it is worth being familiar with 
this as you may see it in existing code. Below is an example of classical mapping, in which we setup a 
Python class for a Species, a table object for the species table, and dynamically map them to each other ::

    # imports are not show in this example
    
    # a plain old Python class with a repr method"
    class Species(object):
        def __repr__(self):
            return "Species: %s" % self.name

    # a table definition, that describes our SQL table
    species_table = Table( metadata, 
        Column('id', Integer, primary_key=True)
        Column('name', String(128), nullable=False)
    )

    # call the mapper function to map them to each other
    mapper(Species, species_table)
    

This differs from an **Active Record** ORM, in which a the domain model class also includes the table
definition information and we always have a one-to-one correspondence between domain 
model classes and database tables. (The Django ORM and the ORM for Ruby on Rails are Active Record ORMs)
Many people find the Active Record pattern easier to read, so SQLAlchemy now provides an
alternate declaration style called  **Declarative Base**. When we use Declarative Base, our domain model
definition *looks* like an Active Record ORM, the table information is contained in the class definition
itself. Under the hood, however, SQLAlchemy is still using the Data Mapper pattern: the class
definition creates a Table object and calls the mapper function to map them together. 
This has the advantage of allowing us the extra flexibility of arbitrarily mapping domain 
model classes to tables should we need this for our application. Below is an example
of using the declarative base method, in which we use the declarative_base function to generate
our domain model's base class. This bass class will take care of generating
our data mapper boilerplate for us ::

    Base = declarative_base()
    
    class Species(Base):
        __tablename__ = 'species'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(128), nullable=False)
        
        def __repr__(self):
            return "Species: %s" % self.name


You can see that this is less typing and easier to follow. Functionally, they are
identical and we can switch between the two patterns any time.

Note that the table describing attributes are specified as *class* attributes, not instance variables:
they are not inside an __init__ method and are not attached to *self*. This pattern of using
class variables as a schema definition language is common in many Python frameworks. 


Engine & Metadata
-----------------
In SQLAlchemy, connections to the database itself are handled through an engine,
which we instantiate by passing in a database connection string ::

    from sqlalchemy import create_engine
    # connect to the database, asking for SQL statements to be echoed to the log
    engine = create_engine('sqlite:///:memory:', echo=True)

Information about our domain model is stored on a MetaData object, which acts
as a **registry** for all our domain model classes. This is accessible as
an attribute on our Base class, **Base.metadata**. The MetaData object keeps track of all classes,
tables, and mappers used in our domain model. The metadata object, however, has no 
reference to specific database until it is bound to the engine. Only when it is bound
to the engine can it actually execute SQL commands to our database. For example,
we can drop all our tables and recreate them by using helper methods on the metadata object,
to which we pass a reference to our engine ::

    # this comes *after* defining our model classes
    # and instantiating our engine
    
    # drop and create all our tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
Normally we can set up the engine and Base class and just forget about them, however
when things aren't working it's very helpful to understand which component is doing what for 
debugging and making sense of the SQLAlchemy stack traces (the error output in the console).
A common error is getting the creation of the different components out of order when refactoring
a single file application into multiple files. It helps to remember the following:

    * when a module is imported, all its code runs
    * we need to create the Base class before defining data model classes
    * we need to create the engine before any calls to metadata methods

If you are having issues sorting out what runs when, use the log to see the order
of execution in your terminal.


Unit of Work and The Session
----------------------------
Once we have our domain model defined, we can start creating objects that we'd like
to have persisted to the database. To recap our example, this is what we have so far ::

    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
   
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base = declarative_base()

    class Species(Base):
        __tablename__ = 'species'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(128), nullable=False)
        
        def __repr__(self):
            return "Species: %s" % self.name


After the above has executed, we can create some species objects. Note that we have not defined an init method,
but the Base class gives us one that will take keyword args and set them 
as attributes on the object, so we can do the following ::

    cat = Species(name="Cat")     

This creates a cat object, but does it write to the database? 
If we trace through our code, we can see that:
    
    * we have an engine, connected to our database
    * we have defined a domain model, with classes registered in the metadata registry at Base.metadata
    * we have created an object using this class, which we know has a connection to the metadata through the 
      parent class

However, we don't have the metadata connected to the engine anywhere, so our new object
has no way of actually getting to the database. This is the job of the **Session**. 

The Session acts as the intermediary between our data model and our actual database. It binds an
engine to a metadata registry, and keeps track
of objects that should be persisted, tracking whether they have changed, and ultimately 
generating and executing the SQL commands.

We see a factory function used again to get our Session *class*, and this class is then
used to generate our session object, that is used for one interactive session of reading
and writing to the database. Normally we will only be using one engine and
one session at a time, but SQLAlchemy is designed to be flexible enough to work with
multiple databases at once, so it is conceivable that one might have multiple session
factories and session handlers. In the example below, we build our Session class with
the **sessionmake** function and then instantiate a local session object using the 
Session class ::

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
We can then use this session object to query our database and to persist new objects
to the database by adding them to the session. Queries will execute immediately,
but adding new objects to the db or updating existing objects requires us to
to **commit the session**. At that point, the SQL for creation and update is
executed. When we are done with our session, we close it. ::

    # now we can use db_session to execute queries
    # cound our species, this query executes immediately
    num_species = db_session.query(Species).count()

    # make a new species and add to the session
    dog = Species(name='Dog')
    db_session.add(dog)
    rabbit = Species(name='Rabbit')
    db_session.add(rabbit)
    
    # commit: generate and executing the SQL to create dog and rabbit
    db_session.commit()

    # all done, close the session object
    db_session.close()


Unit of Work
------------
In the example above, we see that the session is used to keep track of new items
we want to persist: we add them to the session, and when we are done, we ask the 
session to commit, at which point all the SQL for generating every new object in 
the session is executed. This is called the Unit of Work pattern: 
the session keeps a running tally for us of everything
that should result in a database change then executes all the pending changes at once
on commit.  This makes it easy for us to make many changes in Python code but know
that they will all either work or be rolled back on error. For example, here we
create a species and edit a species, try to commit, and rollback our changes
on any error. Note that in the example below, the rabbbit species does not
need to be added to the session for saving because we retreived it from the
database using the sessions query attribute. In this case the rabbit species
is already tracked by the session object and changes will be written to our
db when we commit ::

    # create a session object
    db_session = Session() 
    
    # retrieve the rabbit species, automatically in the session
    rabbit = db_session.query(Species).filter_by(name='Rabbit').one()

    # edit rabbit, does NOT write changes at this point
    rabbit.name = 'Bunny Rabbit'
    
    # create hamster
    hamster = Species(name='Hamster')
    session.add(hamster)

    # commit, creating hamster and updating rabbit
    try:
        db_session.commit()
    except:
        # on error, neither hamster creation or rabbit edit will be persisted    
        db_session.rollback()
    finally:
        db_session.close()        


Identity Map
------------
The session is also smart about keeping track of instances of objects that come from the database.
It does this by keeping an Identity Map of all instances of our domain model classes.
This allows the session to know that if we query the session in two different sections of code
and get two seperate references to objects that correspond to the same database record, the
objects should actually be identical. 



    
    
