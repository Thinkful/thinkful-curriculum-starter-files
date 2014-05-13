"""sqla_1_todo.py - a complete sqalalchemy script with extension instructions"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

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


# Extending our basic sqlalchemy script:
#
# 1) Allow passing in a database connection string as a command line 
#   argument to the script.
#
# 2) Add the Pet model, including a foreign key to breed
#
# 3) Add a Person model and a many-to-many table for pets_persons, 
#    with mapped relationships on both Pet and Person (Pet.persons, Person.pets) 
#    Configure the relationship  to ensure that when a pet is deleted or a person 
#    deleted, no dangling entries are left in persons_pets
#
# 4) Add a model for Pet Shelters
#
# 5) Alter the Pet model to include:
#    - a relationship to the shelter that the pet is at or came from
#    - a flag indicating whether the Pet has been adopted 
#
# 6) Write a function, 'adopt_pet':
#   - params: a session, a pet name, and a person first and last name 
#   - updates all tables properly for a person adopting this pet
#     and commits to the database
#   - alter the main body of the script to use this function
#
# 7) Write a method on the shelter class, 'Shelter.check_for_pets'
#   - takes a string parameter, of *either* breed or species
#   - takes an *optional* parameter, 'adopted', with default False
#   - returns a list of all pets available for adoption
#   - if passed the adopted flag, returns a list of pets already adopted
#     from the shelter
#   - alter the main body to call this method
#

# XXX: do we want them writing unit tests for these? or should we save
# that for once we get into Flask?

# we haven't covered the cascade?? what should happen here
# we should probably ensure that deleting a species deletes all it's breeds


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
    
    # count our starting species & breeds
    num_species = dbs.query(Species).count()
    num_breeds = dbs.query(Breed).count()
    log.info("starting with %i species and %i breeds" % (num_species, num_breeds) )

    log.info("\nCreating Species: Cat and Dog (Transient)")
    cat = Species(name="Cat")
    dog = Species(name="Dog")
    
    # we can verify that cat and dog do not have ids yet.
    # pdb.set_trace()
    assert cat.id == None
    assert dog.id == None
    
    # add them to the session and commit to save to db
    dbs.add_all( [cat, dog] )
    dbs.commit()

    # now they have ids
    assert cat.id != None
    assert dog.id != None

    # let's use that id to make a breed
    poodle = Breed(name='Poodle', species_id=dog.id)
    lab = Breed(name='Labrador Retriever', species_id=dog.id)
    golden = Breed(name='Golden Retriever', species_id=dog.id)

    # dog.breeds is still empty, as we have saved the above
    assert dog.breeds == []
    dbs.add_all( [poodle, lab, golden] )
    dbs.commit()

    # now dog.breeds contains lab, poodle, & golden
    # we can use set to assert on membership disregarding order in list
    assert set( [poodle,lab,golden] ) == set( dog.breeds )

    # remove lab from dog.breeds
    dog.breeds.remove(lab)
    dbs.commit()
    # we can see that updating the relationship has updated Lab.species_id to null
    assert lab.species_id == None


    # let's make a new species, parrot and a new breed, Norwegian Blue
    # instead of building our relationship with the 'species_id' field,
    # we will use the 'species' relationship
    # Note: we can use the species parrot, even though it has no ID
    # and has not yet been persisted, the Identity Map can manage all of it

    norwegian_blue = Breed(name="Norwegian Blue",
        species=Species(name="Parrot") 
    )
    parrot = norwegian_blue.species
    african_grey = Breed(name="African Grey", species=parrot)
    
    # in this case, if we check norwegian_blue's species, it already
    # has a functioning reference to Parrot, even though neither has an ID!
    assert norwegian_blue.species == parrot
    assert norwegian_blue, african_grey in parrot.breeds 
    assert (norwegian_blue.id, african_grey.id, parrot.id) == (None, None, None)

    # we can edit using the relationship even though nothing is persisted yet
    parrot.breeds.append( Breed(name="Spix's Macaw") )
    norwegian_blue.name = "Norwegian Blue, Sleeping"
  
    # we only need to add parrot to the session, all parrot breeds that
    # are attached will automatically get added too
    dbs.add(parrot)
    # now when we commit, parrot and all parrot breeds are updated 
    dbs.commit()
   
    # ask the db how many breeds we have
    num_breeds = dbs.query(Breed).count()
    assert num_breeds == 6
    log.info(" num breeds now: %i" % num_breeds)

    # close our session and make a brand new one
    dbs.close()
    dbs = Session()


    # Now for some querying

    # query for all species named Dog
    log.info("querying for species named 'Dog' ")
    # get the results as a list, using filter
    species_list = dbs.query(Species).filter(Species.name == 'Dog').all()
    log.info("Dog species as list: %s" % species_list)
    
    # query for a species named Rabbit, asking for one item or None
    rabbit = dbs.query(Species).filter(Species.name == 'Rabbit').first()
    log.info("Rabbit found: %s" % rabbit)

    # query for a species named Horse, with filter_by kwargs
    # ask for only one
    from sqlalchemy.orm.exc import NoResultFound
    try:
        horse_species = dbs.query(Species).filter_by(name='Horse').one()
    except NoResultFound, e:
        log.info("No species found named 'Horse', exception: %s" % e)

    # query with a join, we want to find a *Breed*, but want to filter on 
    # an attribute of Species
    parrot_breeds = dbs.query(Breed).join(Species) \
      .filter(Species.name=='Parrot').all()
    log.info("Parrot_breeds: %s" % parrot_breeds)

    # an example of reusing a query object
    dog_breed_query = dbs.query(Breed).join(Species) \
      .filter(Species.name=='Dog')
    
    # now we can build on our dog breed query for other queries
    num_dog_breeds = dog_breed_query.count()
    log.info("Number of dog breeds: %i" % num_dog_breeds)

    all_dog_breeds = dog_breed_query.all()
    log.info("All dog breeds: %s" % all_dog_breeds)

    # filter the dog breed query further, generating a new query
    # as this query has already joined Species, we can filter further on species
    retriever_breed_query = dog_breed_query.filter( Species.name.like('%Retriever%') )
    num_retriever_breeds = retriever_breed_query.count()
    log.info("Number of Retriever dog breeds: %s" % num_retriever_breeds)
    all_retrievers = retriever_breed_query.all()
    log.info("Retriever breeds: %s" % all_retrievers)

    # more filter options are documented at:
    # http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#common-filter-operators

    pdb.set_trace()
    log.info("all done!")
