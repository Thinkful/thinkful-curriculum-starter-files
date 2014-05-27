"""pets_model.py - importable model for the pet script"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Text

from sqlalchemy.orm import sessionmaker

import pdb

################################################################################
# Domain Model

Base = declarative_base()

class Species(Base):
    """
    domain model class for a Species
    """
    __tablename__ = 'species'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "%s" % self.name                   


class Breed(Base):
    """
    domain model class for a Breed
    has a with many-to-one relationship Species
    """
    __tablename__ = 'breed'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    species_id = Column(Integer, ForeignKey('species.id') ) 

    species = relationship("Species", backref=backref('breeds', order_by=name) )           

    def __repr__(self):
        return "%s:%s" % (self.name, self.species) 


class Shelter(Base):
    """
    domain model class for a shelter
    """
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    website = Column(Text)
    phone = Column(Text)

    def __repr__(self):
        return self.name



# our many-to-many association table, in our model *before* Pet class 
pet_person_table = Table('pet_person', Base.metadata,
    Column('pet_id', Integer, ForeignKey('pet.id'), nullable=False),
    Column('person_id', Integer, ForeignKey('person.id'), nullable=False)
)


class Pet(Base):
    __tablename__ = 'pet'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    age = Column(Integer)
    dead = Column(Boolean)
    adopted = Column(Boolean)
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
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text)
    phone = Column(Text)
    
    # mapped relationship 'pets' from backref on Pet class 
    
    def __repr__(self):
        return self.name



################################################################################
if __name__ == "__main__":
    # if run this model file as the main script, it will initialize our database

    confirm = raw_input( "Running this file as a main script will drop and "
        "recreate all the tables in the pet database. Continue? (Y/N): ")
    if confirm not in ('Y','y','Yes','yes'):
        print "aborting db init, exiting."
        sys.exit()

    db_url = 'sqlite:///pets_code_along.db'
    # create an engine
    engine = create_engine(db_url, echo=True)
    # drop all tables and recreate
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    print "Database initialized, exiting."
