SQLAlchemy - Conceptual Overview
================================

SQLAlchemy is very flexible and powerful toolkit, and is designed so you won't "outgrow" it  
as your application or database becomes more complex. The cost of this flexibility is that we
encounter some advanced programming concepts and architechtural decisions. 
Understanding SQLAlchemy is easier if these **Design Patterns** are understood at the outset,
and if the role of the different components in play is clear.

The term "Design Pattern" is used by programmers to describe an common architectural approach
to a solve a problem, described in a language agnostic fashion. Design Patterns enable programmers
to communicate about problems and architecture at a higher abstract level without getting bogged
down in code details. SQLAlchemy uses a number of design patterns and discusses these in the
documentation. We don't need to understand exactly how they work, but it's helpful to have a 
general idea of what a design pattern is to make reading the SQLAlchemy documentation easier.

Factory Functions
-----------------
SQLAlchemy uses Factory Functions to dynamically generate classes. In Python, a class is itself a first
class object: it can be stored in a variable, returned from a function, and dynamically assembled by other code. 
This is in contrast to compiled statically typed langugages like C or Java. A class in Python is really
just a callable object that, when called, returns a new object: the instantiation of the class. 
We use the convention of writing classes capitalized to make their role clear. The Species class is an object
that gets called to return a new species object. A class *itself* can also be built and returned by a function,
and this is often used when the class has dependencies that can not be determined
until *runtime*.  In SQLAlchemy we see these factory functions 
used to build our data model base class and also to build the Session class. 

The main thing to beware of here is to watch your capitalization; remember that the returned objects
are classes and should begin with upper case letters. ::

    # import the declarative_base factory function
    from sqlalchemy.ext.declarative import declarative_base

    # dynamically build our base class
    Base = declarative_base()

    # now use our base class
    class Pet(Base):
        ...etc...

Once the Base class has been returned by the factory function, it is used as normal just as
if it had been imported. We'll see another factory function later when dealing with the
Session object.


Data Mapper & Declarative Base
------------------------------
SQLAlchemy uses a pattern called **Data Mapper** to persist objects. In the Data Mapper pattern, 
we create a set of regular Python classes corresponding to the real world classes of objects that we are
persisting in the database, such as Species, Pet, and Person. Each instantiation of a class represents
one database record: there will be a Person object for Ben, and a series of pet objects for Ben's cats. This 
collection of classes is referred to as our **Domain Model**. 

A separate set of objects representing the database *tables* are also 
created, one per table, and these are then **mapped** dynamically to our domain model classes using
SQLAlchemy's **mapper** function.  The Data Mapper pattern is very flexible because it doesn't 
make any assumptions about how our Python classes are mapped to our tables: 
if the database grows and we need to change our table structure or even how many 
tables are mapped to each class, we can easily do so without affecting code that is already 
using the domain model objects.

SQLAlchemy supports two different ways of setting up your domain model and data mappers.
In **Classical Mapping**, the three components are declared separately (domain model classes, table objects,
and mapper objects).  Older versions of SQLAlchemy only supported classical mapping, so it is worth being familiar with 
this as you may see it in existing code. You will also find that frequently in programming as a problem becomes more
complex and an application grows, we wind up preferring options that involved writing more code if the result
is increased clarity and flexibility. All software architecture decisions involve trade offs, and it's wise
to distrust anyone saying that one style is always the best! That which is the most effective use of 
resources for a small project with a manageable number of domain model classes and a limited database is not
necessarily the best us of resources for a project like Amazon. 

Some programmers prefer classical mapping for very complex databases or 
for situations where they are not in control over the database strucure. Below is an example of classical mapping,
in which we setup a Python class for a Species, a table object for the species table, and dynamically map them to each other ::

    # imports are not show in this example
    
    # a plain old Python class with a repr method
    class Species(object):
        def __repr__(self):
            return "Species: %s" % self.name

    # a table object describing our species table
    species_table = Table( metadata, 
        Column('id', Integer, primary_key=True)
        Column('name', String(128), nullable=False)
    )

    # call the mapper function to map them to each other
    # this might even happen in a different module, so long as the
    # above class and table have been imported
    mapper(Species, species_table)
    

This pattern differs from an **Active Record** ORM, in which the domain model class also includes the table
definition and we always have a one-to-one correspondence between domain 
model classes and database tables. (For example, the Django ORM and the ORM for Ruby-on-Rails are Active Record ORMs.)
Many people find the Active Record pattern easier to read and less work to setup, so SQLAlchemy now provides an
alternate declaration style called  **Declarative Base**. When we use Declarative Base, our domain model
definition *looks* like an Active Record ORM: the table information is contained in the class definition
itself. However, under the hood, SQLAlchemy is still using the Data Mapper pattern: the class
definition actually creates a separate table object and calls the mapper function to map them together. 
This has the advantage of allowing us the extra flexibility of arbitrarily mapping domain 
model classes to tables should we need it later as complexity grows. We can move anytime between Classical
Mapping and Declarative Base. Below is an example
of using the declarative base method, in which we use the declarative_base factory function to generate
our domain model's base class. This base class then  generates our data mapper boilerplate for us ::

    Base = declarative_base()
    
    class Species(Base):
        __tablename__ = 'species'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(128), nullable=False)
        
        def __repr__(self):
            return "Species: %s" % self.name

        # an optional constructor that sets attributes from kwargs
        def __init__(self, **kwargs):
            for key,value in kwargs.items():
                setattr(self, key, value)

You can see that this is less typing and easier to follow. But functionally, they are
identical and we can switch between the two patterns any time. You will find that most recent example code
for SQLAlchemy uses Declarative Base.

Note that the table describing attributes are specified as *class* attributes, not instance variables:
they are not inside an __init__ method and are not attached to *self*. This pattern of using
class variables as a schema definition language is common in many Python frameworks. You may
be asking yourself how this is possible, we can see the constructor and it's not doing anything
unusual. The answer is that Base class uses a *metaclass* that changes how the class itself is constructed; it 
adds a stage that SQLAlchemy calls **Instrumentation** in which the named Column attributes are
turned into a table object and a mapper is called using the class and the table object. We don't
need to concern ourselves further with *how* instrumentation happens as long as we understand
that the resulting objects are special objects with mappers already attached and that they 
work functionally the same way as classical mapping.


Engine
------
In SQLAlchemy, connections to the database itself are handled through an engine,
which we instantiate by passing in a database connection string, and some optional
flags. ::

    from sqlalchemy import create_engine
    # connect to the database, asking for SQL statements to be echoed to the log
    engine = create_engine('sqlite:///:memory:', echo=True)

By passing in a True flag for echo, we can see all the resulting SQL in the terminal
as our application runs. The engine variable we have created will act as our handle
to the actual database, before information from our domain model can get to the database,
we will need to attach our domain model somehow to an instantiated engine.


The MetaData Object
-------------------
All the information describing our domain model is collected in one master registry,
an instance of the SQLAlchemy **MetaData** class normally named **metadata**. 
The MetaData object keeps track of all classes, tables, and mappers used in our domain model,
it is how the domain model classes are aware of each other and of each other's tables for
managing relationships between tables and classes. Only one metadata object gets created for
your domain model, it's the train station for the domain model. ::

When using classical mapping, you will explictly create this metadata object using 
the MetaData class, and you'll pass it as a paramater when creating table objects. ::

    metatada = MetaData()
    
    species_table = Table('species', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', Text, nullable=False)
    )    
    pet_table = Table('pet', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', Text, nullable=False)
        ... etc ...
    )
        
When using declarative base, the metadata object is created for us by the declarative 
base factory function, and it's attached to the Base class as an attribute: **Base.metadata**.
It's still the same thing, our one and only domain model registry. If you are looking
at examples of SQLAlchemy code, you may encounter mixtures of both classical mapping
and declarative base mapping, just remember that you need to replace references to 
**metadata** with **Base.metadata** if you created the metadata object implicityly as
part of your declarative base function instead of explicitly with the MetaData class 
(and of course the reverse).

Binding MetaData
----------------
Once our domain model classes and tables are created, we can get at them all 
through the metadata registry. However, the metadata has no reference to a specific
database: it has not been connected to our engine. In SQLAlchemy, connecting metadata 
to an engine is called **binding**. This can happen explicitly in classical mapping,
or implicitly in declarative base mapping, but it has to happen *somewhere* before
any SQL can get to our database.

An example of this happening implicity is shown below, using the Base classes metadata
reference to drop and create all our tables in a database. We pass a reference to
an engine in as a paramater and the binding happens in the method call ::

    # this comes *after* defining our model classes
    # and instantiating our engine
    
    # drop and create all our tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

Dropping and creating tables is not something we do every day of course. 
In normal use, we use another component to manage the binding between our database
engine and domain model, the **Session**. We'll get to the session shortly
after a brief detour to recap where we are so far. 

At this point, we have our domain model defined, and we can start creating objects that we'd like
to have persisted to the database. ::

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

        # we don't need to make an init method
        # Base actually gives us one free that sets kwargs as attributes

    # now we make some objects
    # SQLAlchemy will take care of generating the primary key for us
    cat = Species(name="Cat")     
    dog = Species(name="Dog")


This creates a cat and dog object, but does it write to the database? 
If we trace through our code, we can see that:
    
    * we have an engine, handling our connection to our database
    * we have defined a domain model, registered in the metadata object at Base.metadata
    * we have created some object using our domain model class

However, we have not yet bound the metadata to the engine anywhere, so our new object
has no way of actually getting to the database. This is where the **Session** comes into play.


The Session
-----------
The Session acts as the intermediary between our data model and our actual database. It binds an
engine to a metadata registry, and keeps track of all the objects that should be persisted. It 
manages creating or deleting objects when we retrieve an object from the database using a query, and
it tracks whether any objects we have created or retreived have changed. When we ask it
to save, it takes care of generating and executing the SQL commands for creation, update,
or delete of objects. 

We see a factory function used again to get our Session *class*, and this class is then
used to generate a session object, used for one interactive session of reading
and writing to the database. (Normally we will only be using one engine and
one session at a time, but SQLAlchemy is designed to be flexible enough to work with
multiple databases at once, so it is conceivable that one might have multiple session
factories and session handlers.) In the example below, we build our Session class with
the **sessionmake** factory function and then use it to instantiate a local session object,
passing in a reference to the engine to use in binding. Our local variable, **db_session**,
will be used as our database handle for the duration of our script :: 

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db_session = Session()

# TODO: demonstrate how to do this if engine has not been created at time of sessionmaker call


We can now use our session object to query our database to get objects, and to persist new objects
to the database by adding them to the session. Queries will execute immediately,
but adding new objects to the db or updating existing objects requires us to
to **commit the session**. At that point, the SQL for creation and update is
executed. When we are done with our session, we close it. ::

    # now we can use db_session to execute queries
    
    # count our species, this query executes immediately
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


The astute reader may wonder again where we made our connection between our
metadata and the engine. The session can't do anything until it receives 
either classes or objects created with our domain model classes. It is through
these classes or objects that it has access to the metadata. In the case of
queries, we pass in a class as an argument ::
    
    num_species = db_session.query(Species).count()

And in the case of creating objects, we add the instantiated object to the 
session ::

    rabbit = Species(name='Rabbit')
    db_session.add(rabbit)
    

Session States
--------------
Any instances of our domain model classes will have a **Session state** relative 
to the session: they can be **transient**, **pending**, **persistent**, or **detached**.

When we create our rabbit object, it gets created in the Transient state. It has
no corresponding record in the database, and thus the value of **rabbit.id** is None.
Because we haven't added it to the session, if we exit our script before adding the rabbit
to the session, no rabbit record gets saved. Dog gets added to the session and thus on
commit it gets persisted and then as an ID value corresponding to the database primary key ::

    # make the dog species and rabbit species 
    dog = Species(name='Dog')
    rabbit = Species(name='Rabbit')

    # dog and rabbit are transient and have no DB id
    assert dog.id == None
    assert rabbit.id == None

    # add dog to the session, but not rabbit
    # dog is now in the Pending state, will be persisted on next commit
    db_session.add(dog)

    # dog is Pending, but id is still None!        
    assert dog.id == None    

    # commit: generate and executing the SQL for dog only
    db_session.commit()

    # dog is now in the Persistent state, and has a db id 
    assert dog.id != None

    # all done, close the session object, no rabbit created
    db_session.close()

    # rabbit is still transient, did not get persisted and is discarded on exit
    assert rabbit.id == None


If you are having troubles figuring out what state an object is in you can
use the SQLAlchemy **inspect** function ::

    from sqlalchemy import inspect
    dog_inspection = inspect(dog)
    log.debug(" dog is persistent? %s" % dog_inspection.persistent )


For completeness we'll mention that the final state is **Detached**,
meaning the object has a record in the database
but is not in the session. This can happen if you remove a retreived object
from a session, but isn't something we'll concern ourselves with further here.



Unit of Work and the Indentity Map
----------------------------------
In the example above, we see that the session is used to keep track of new items
we want to persist: we add them to the session, and when we are done, we ask the 
session to commit, at which point all the SQL for generating every new object in 
the session is executed. This is called the Unit of Work pattern: 
the session keeps a running tally for us of everything
that should ultimately result in a database change, and then executes all the pending changes at once
as one unit on a commit or flush. 

This makes it possible for us to make many changes in Python code, distributed
among different methods even, but know
that they will all either work or be rolled back on error. In the example below we
create a species and edit a species, try to commit, and rollback our changes
on any error. Note that in the example below, the rabbbit species does not
need to be added to the session for saving because we retreived it from the
database using the session; it's already in our session object's map of tracked objects
and begins in the Persistent state. This also means that any changes to the
rabbit will be written to the database on the next commit or flush. ::

    # create a session object
    db_session = Session() 
    
    # retrieve the rabbit species, 
    # it's automatically in the session and has state Persistent
    rabbit = db_session.query(Species).filter_by(name='Rabbit').one()

    # we can look at rabbit's ID:
    log.debug("retrieved rabbit, id: %s" % rabbit.id)

    # edit rabbit, does not write changes to db yet
    rabbit.name = 'Bunny Rabbit'
    
    # create hamster, add it to the session
    hamster = Species(name='Hamster')
    guinea_pig = Species(name='Guinea Pig')
    # add both new items at once
    session.add_all( [hamster, guinea_pig] )
    
    # commit, creating hamster/guinea_pig & updating rabbit in the database
    try:
        db_session.commit()
    except:
        # rollback on error, 
        # neither hamster/guinea_pig creation nor rabbit edit will be persisted    
        db_session.rollback()
    finally:
        db_session.close()        


The session is also smart about keeping track of instances of objects that come from 
or should be persisted to the database. It does this by keeping an **Identity Map** of
all the objects persisted in the database. 
This allows the session to know that if we query the session in two different sections of code
and get two seperate references to objects that correspond to the same database record, the
objects should actually be identical and should be treated as equal.
 



    
    
