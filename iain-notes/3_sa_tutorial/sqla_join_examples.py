"""sqla_2.py - a complete sqalalchemy script"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Text

from sqlalchemy.orm import sessionmaker

import pdb
import logging
log = logging.getLogger(__name__)

################################################################################
# set up logging - see: https://docs.python.org/2/howto/logging.html

# when we get to using Flask, this will all be done for us
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
log.addHandler(console_handler)


################################################################################
# Domain Model

Base = declarative_base()
log.info("base class generated: %s" % Base)

# define our domain model

class Breed(Base):
    """
    domain model class for a Breed
    has a with many-to-one relationship Species
    """
    __tablename__ = 'breed'

    # database fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    #species_id = Column(Integer, ForeignKey('species.id'), nullable=False ) 
    species_id = Column(Integer, ForeignKey('species.id') ) 

    # mapped relationships
    species = relationship("Species", backref=backref('breeds', order_by=name, 
        cascade="all, delete, delete-orphan") )           

    # methods
    def __repr__(self):
        return "%s:%s" % (self.name, self.species) 

class Species(Base):
    """
    domain model class for a Species
    """
    __tablename__ = 'species'

    # database fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    #breeds = relationship("Breed", backref=backref("species") )
    
    # methods
    def __repr__(self):
        return "%s" % self.name                   


class Shelter(Base):
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    website = Column(Text, nullable=False)

    def __repr__(self):
            return self.name

# our many-t0-many association table, in our model *before* Pet class 
pet_person_table = Table('pet_person', Base.metadata,
    Column('pet_id', Integer, ForeignKey('pet.id'), nullable=False),
    Column('person_id', Integer, ForeignKey('person.id'), nullable=False)
)


class Pet(Base):
    __tablename__ = 'pet'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    breed_id = Column(Integer, ForeignKey('breed.id'), nullable=True ) 
    shelter_id = Column(Integer, ForeignKey('shelter.id'), nullable=True ) 

    # must be nullable, as some pets will be the roots of our trees!
    parent_id = Column(Integer, ForeignKey('pet.id'), nullable=True ) 

    # NB: we must specify the remote side for the many-to-many backref to work
    children = relationship('Pet', backref=backref('parent', remote_side=[id]) )

    # mapped relationship, pet_person_table must already be in scope!
    people = relationship('Person', secondary=pet_person_table, backref='pets')
   
    breed = relationship('Breed', backref='pets')
    shelter = relationship('Shelter', backref='pets')
 
    def __repr__(self):
        return self.name       


class Person(Base):
    __tablename__ = 'person'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    
    # mapped relationship 'pets' from backref on Pet class 
    
    def __repr__(self):
        return self.name


################################################################################
def init_db(engine):
    "initialize our database, drops and creates our tables"
    log.info("init_db() engine: %s" % engine)
    
    # drop all tables and recreate
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    log.info("  - tables dropped and created")



if __name__ == "__main__":
    log.info("main executing:")              

    # create an engine
    # TODO: allow passing in a db connection string from a command line arg
    #engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///sqla_4.db', echo=True)
    log.info("created engine: %s" % engine)

    # if we asked to init the db from the command line, do so
    if True:
        init_db(engine)

    # call the sessionmaker factory to make a Session class 
    Session = sessionmaker(bind=engine)
    
    # get a local session for the this script
    dbs = Session()
    db_session = dbs
    log.info("Session created: %s" % dbs)

    # create our cat species and persian breed
    cat = Species(name="Cat")
    persian = Breed(name="Persian", species=cat)
    tabby = Breed(name="Tabby", species=cat)

    dbs.add(cat)
    dbs.commit()
    log.info("saved 'em both")
    assert cat.id
    assert persian.id

    spca = Shelter(name="SPCA", website="www.spca.com" )
    # create some pets and persons
    jackson_parent = Pet(name="Jack", breed=tabby, shelter=spca)
    jackson = Pet(name="Jackson", breed=persian, shelter=spca, parent=jackson_parent )
    iain = Person(name="Iain")
    iain.pets.append(jackson)
    
    dbs.add_all( [jackson, jackson_parent, iain, spca] )
    dbs.commit()
    dbs.close()
    # get a brand new session for our queries
    dbs = Session()
    
    log.info("ready:")
    
    cat_shelters = dbs.query(Shelter
        # pet.shelter_id == shelter.id
        ).join(Pet       
        # pet.breed_id == breed.id
        ).join(Breed
        # breed.species_id == species.id
        ).join(Species
        # species.name == 'Cat'                
        ).filter(Species.name=="Cat").all() 

    log.info("cat shelters: %s" % cat_shelters)
    
    # we want to retrieve pets, so Pet is the root of the query
    spca_cats = dbs.query(Pet
        # pet.shelter_id == shelter.id
        ).join(Shelter       
        # pet.breed_id == breed.id
        ).join(Breed
        # breed.species_id == species.id
        ).join(Species
        # species.name == 'Cat'                
        ).filter(Species.name=="Cat"
        # shelter name == 'SPCA'
        ).filter(Shelter.name=="SPCA"
        ).all()  
    log.info("spca cats: %s" % spca_cats)

    # join specifies the attribute of Pet that we are joining on
    jackson_people = db_session.query(Person
        ).join(Pet, Person.pets
        ).filter( Pet.name == 'Jackson' ).all()
    log.info(" jackson_people: %s" % jackson_people)
    
    # query for people across the many-to-many of pets to people,
    # filtering on column attribute of Pet
    jackson_people = db_session.query(Person
        ).filter( Person.pets.any( Pet.name == 'Jackson') ).all()
    log.info(" jackson_people verson 2: %s" % jackson_people)

    # join specifies the attr of Person that we join on
    persian_cat_people = db_session.query(Person
        ).join(Pet, Person.pets
        ).join(Breed
        ).join(Species
        ).filter(Breed.name=='Persian'
        ).filter(Species.name=='Cat'
        ).all()
    log.info(" persian_cat_people: %s" % persian_cat_people)
    
    # get the cat who's parent is named jackson
    from sqlalchemy.orm import aliased
    PetParent = aliased(Pet)
    children = db_session.query(Pet
        # join from Pet.parent to the aliased table
        ).join(PetParent, Pet.parent
        # filter on the *parents* attribute, in the alias
        ).filter(PetParent.name=='Jack'
        ).all()
    log.info(" pet's with a parent named 'Jack': %s" % children )

    # get people who have pets who have parents
    # we want to get people, so start with Person
    PetParent = aliased(Pet)
    people = db_session.query(Person
        # our M2M join from Person.pets to the Pet table
        ).join( Pet, Person.pets
        # now join from Pet.parent to the aliased table
        ).join( PetParent, Pet.parent
        ).all()
    log.info(" people with pets who have parents: %s" % people)


    # get people who have pets who have parents who are persian
    PetParent = aliased(Pet)
    people = db_session.query(Person
        # our M2M join from Person.pets to the Pet table
        ).join( Pet, Person.pets
        # now join from Pet.parent to the aliased table
        ).join( PetParent, Pet.parent
        ).join( Breed, PetParent.breed
        ).filter( Breed.name == 'Tabby' 
        ).all()
    log.info(" people with pets who have Tabby parents: %s" % people)

    # get people who have pets who have parents of breed Tabby
    PetParent = aliased(Pet)
    BreedOfParent = aliased(Breed)
    people = db_session.query(Person
        # our M2M join from Person.pets to the Pet table
        ).join( Pet, Person.pets
        # now join from Pet.parent to the aliased table
        ).join( PetParent, Pet.parent
        # NEW: highlight we're after the Parents breed
        ).join( BreedOfParent, PetParent.breed
        ).filter( BreedOfParent.name == 'Tabby' 
        ).all()
    log.info(" people with pets who have Tabby parents: %s" % people)
    
    # get people who have Persian pets who have parents of breed Tabby
    PetParent = aliased(Pet)
    BreedOfParent = aliased(Breed)
    people = db_session.query(Person
        # our M2M join from Person.pets to the Pet table
        ).join( Pet, Person.pets
        # now join from Pet.parent to the aliased table
        ).join( PetParent, Pet.parent
        # join the breed table to filter on the child pet
        ).join( Breed, Pet.breed
        # also join the aliased Breed table for the Parent Breed filter
        ).join( BreedOfParent, PetParent.breed
        # filter on child breed
        ).filter( Breed.name == 'Persian'
        # filter on parent breed 
        ).filter( BreedOfParent.name == 'Tabby' 
        ).all()
    log.info(" people with Persian pets who have Tabby parents: %s" % people)

    # long build up
    # often you'll see variables holding a class written as klass
    klass = Person
    filter_dict = {
        'name': 'Iain',
        'email': 'Iain@email.com',
        'phone': '123-456-7890', 
        'age': 39, 
    }
    # build a query up iteratively
    # start with our base query object
    query = db_session.query(klass)
    # loop through the dictionary, creating a filter for each
    # attribute in the dictionary that is an attr of Person
    for attr, value in filter_dict.items():
        # this means age won't get used as its not in our table
        if hasattr( klass, attr ):
            query = query.filter( getattr(klass, attr) == value)
    # now we execute our query
    iains = query.all()
    log.info(" iains: %s" % iains)

    # long search #2 
    search_dict = {
        'name': 'Jackson',
        'breed_name': 'Persian',
    }
    # base query
    query = db_session.query(Pet)
    # go through our dict, joining when necessary
    # we only filter if the dict has a value for the key
    # name
    if search_dict.get('name',None):
        pet_name = search_dict['name']
        query = query.filter( Pet.name == pet_name )
    # breed
    if search_dict.get('breed_name', None):
        breed_name = search_dict['breed_name']
        # join breed
        query = query.join(Breed
            # then filter on Breed
            ).filter(Breed.name == breed_name)         
    items = query.all()
    log.info("items: %s" % items)

    pdb.set_trace() 

    log.info("all done!")
