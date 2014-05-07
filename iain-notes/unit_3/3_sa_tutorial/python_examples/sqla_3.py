"""sqla_3.py - a complete sqalalchemy script"""

# this one tests association relationships

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
class Species(Base):
    """
    domain model class for a Species
    """
    __tablename__ = 'species'

    # database fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # methods
    def __repr__(self):
        return "%s" % self.name                   


class Breed(Base):
    """
    domain model class for a Breed
    has a with many-to-one relationship Species
    """
    __tablename__ = 'breed'

    # database fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    species_id = Column(Integer, ForeignKey('species.id') ) 

    # mapped relationships
    species = relationship("Species", backref=backref('breeds', order_by=name) )           

    # methods
    def __repr__(self):
        return "%s:%s" % (self.name, self.species) 



class Pet(Base):
    __tablename__ = 'pet'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    
    # must be nullable, as some pets will be the roots of our trees!
    parent_id = Column(Integer, ForeignKey('pet.id'), nullable=True ) 

    # NB: we must specify the remote side for the many-to-many backref to work
    children = relationship('Pet', backref=backref('parent', remote_side=[id]) )

    def __repr__(self):
        return self.name


class Person(Base):
    __tablename__ = 'person'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    def __repr__(self):
        return self.name

    # a read only property to get all of a person's pets
    @property
    def pets(self):
        log.info("Pets property running")
        return [ assoc.pet for assoc in self.pet_assocs ]

    # check for a pet, returns years of relationship or None if not in list
    # XXX: this one's not working right yet
    def has_pet(self, pet):
        for assoc in self.pet_assocs:
            if assoc.pet == pet:
                return assoc.years  
        return None


class PetPersonAssoc(Base):
    __tablename__ = 'pet_person_assoc'
    
    # surrogate primary key
    id = Column(Integer, primary_key=True)

    pet_id = Column(Integer, ForeignKey('pet.id'), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    
    # an integer for capturing years
    years = Column(Integer)

    person = relationship('Person', backref=backref('pet_assocs') )
    pet = relationship('Pet', backref=backref('person_assocs') )

    def __repr__(self):
        return "PetPersonAssoc( %s : %s )" % ( self.pet.name, self.person.name) 
        


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
    engine = create_engine('sqlite:///:memory:', echo=True)
    log.info("created engine: %s" % engine)

    # if we asked to init the db from the command line, do so
    if True:
        init_db(engine)

    # call the sessionmaker factory to make a Session class 
    Session = sessionmaker(bind=engine)
    
    # get a local session for the this script
    dbs = Session()
    log.info("Session created: %s" % dbs)
  
    ginger = Pet(name="Ginger")
    titchy = Pet(name="Titchy")
    iain = Person( name="Iain" )
    iain.pet_assocs.append( PetPersonAssoc(pet=ginger) )
    iain.pet_assocs.append( PetPersonAssoc(pet=titchy) )
    
    dbs.commit()
    pdb.set_trace()

    log.info("all done!")
