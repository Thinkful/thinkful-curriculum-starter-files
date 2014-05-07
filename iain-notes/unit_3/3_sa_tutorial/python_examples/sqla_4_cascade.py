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
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False ) 

    # mapped relationships
    species = relationship("Species", backref=backref('breeds', order_by=name, 
        cascade="all, delete, delete-orphan") )           

    # methods
    def __repr__(self):
        return "%s:%s" % (self.name, self.species) 


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
   
    log.info("deleting cat")
    dbs.delete(cat)
    dbs.commit()
    
    # cat has been deleted now
    # we check in the db terminal session, and it's gone like a train!

    # careful, we still have a non-persisted cat variable in python scope...    
    assert cat and cat.id
    # but if we query the db for cat using its old id, it's not there
    # this wipes out our cat variable and give us an accurate model
    cat = dbs.query(Species).get(cat.id) 
    assert cat == None
    
    # our persian breed is still there though, with an empty species_id column
    assert persian.id
    assert dbs.query(Breed).get(persian.id)
    assert persian.species == None

    
    

    log.info("all done!")
