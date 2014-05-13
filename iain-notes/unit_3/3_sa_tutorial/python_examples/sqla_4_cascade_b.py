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
    


class Person(Base):
    __tablename__ = 'person'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    
    # mapped relationship 'pets' from backref on Pet class 
        


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
    log.info("Session created: %s" % dbs)

    # create our cat species and persian breed
    cat = Species(name="Cat")
    persian = Breed(name="Persian", species=cat)

    dbs.add(cat)
    dbs.commit()
    log.info("saved 'em both")
    assert cat.id
    assert persian.id

    spca = Shelter(name="SPCA", website="www.spca.com" )
    # create some pets and persons
    jackson = Pet(name="Jackson", breed=persian, shelter=spca )
    iain = Person(name="Iain")
    iain.pets.append(jackson)

    dbs.add_all( [jackson, iain, spca] )
    dbs.commit()
   
    log.info("ready:")
    pdb.set_trace()
    

    log.info("all done!")
