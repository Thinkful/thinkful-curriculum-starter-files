Lesson 3 Assignment 3, Domain Model Relationships
=================================================

In the previous assignment we added some new types to our domain models and
added some new classes to our domain model. The real power of the SQLAlchemy ORM
comes from it's flexible handling of mapped relationships, and we've seen the beginning
of this with our many-to-one relationships between Breed and Species and between Pet and 
Shelter. In this assignment we'll explore the details of one-to-many relationships further,
and we'll introduce many-to-many relationships and self-referential parent-child relationships.
We'll also see how we can configure the mappers so that our foreign key constraints
do the right thing when objects are deleted or updated.

One-To-Many Relationships Revisited
-----------------------------------

?Damn, where to put this paragraph?
Having a common naming convention also helps us keep this
straight. SQLAlchemy has no rules about names, but a good practise is to name your primary key
on any given model "id" and name foreign keys as "{table name}_id". The mapped 
relationship is usually named for the class being related to. 

When we create a one-to-many (or many-to-one) relationship in an SQLAlchemy model, we
need two elements: our foreign key, and our mapped property. And we need to 
to make sure the way we define the foreign key makes sense for how we will use the mapped
property. For example, we know that a Breed *must* belong to a species, it makes no logical sense
for a breed not to have a species, thus we can say that the foreign key to the species table
should always have a valid species id.  For example, our breed
and species model ::

    class Species(Base):
        __tablename__ = 'species'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)

    class Breed(Base):
        __tablename__ = 'breed'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        species_id = Column(Integer, ForeignKey('species.id') ) 
        
        species = relationship("Species", backref=backref('breeds', order_by=name) )           

In our code-along for assingment 2, we wanted to make sure that you could experiment with
the results of deleting ends of relationships, but to make a robust model, we should
ensure that species_id can not be null::

    class Breed(Base):
        __tablename__ = 'breed'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        # adding nullable=False to our foreign key column
        species_id = Column(Integer, ForeignKey('species.id'), nullable=False ) 
   
        # mapped relationships
        species = relationship("Species", backref=backref('breeds', order_by=name) )           


With this change, if we try to make a breed without a species id, we'll get an error
when we commit to the database. Below is an example of dropping into PDB during
our script, and creating a Breed without a Species::

    (Pdb) poodle = Breed(name="Poodle")
    (Pdb) dbs.add(poodle)
    (Pdb) dbs.commit()
    2014-04-22 20:13:56,695 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
    2014-04-22 20:13:56,696 INFO sqlalchemy.engine.base.Engine INSERT INTO breed (name, species_id) VALUES (?, ?)
    2014-04-22 20:13:56,696 INFO sqlalchemy.engine.base.Engine ('Poodle', None)
    2014-04-22 20:13:56,696 INFO sqlalchemy.engine.base.Engine ROLLBACK
    *** IntegrityError: (IntegrityError) breed.species_id may not be NULL u'INSERT INTO breed (name, species_id) VALUES (?, ?)' ('Poodle', None)
    (Pdb) 
    
With our new definition for the species_id foreign key, we must either specify
a species_id, or add a related species to the mapped relationship. Both the 
below will work:

    # assuming dog is a valid species variable

    # use the id from the dog variable for the species_id
    Poodle = Breed(name='Poodle', species_id=dog.id)

    # use the dog object as the species arg
    poodle = Breed(name='Poodle', species=dog)
        
Generally the second style is preferable as it can be used even if the dog
object has not yet been persisted and thus has no id.

Once we've created poodle, we have access to the dog species object
at **poodle.species**. Conversely, we can also access all the breeds 
that use a species though the species object's 'breeds' attribute, as
we've specified this as a **backreference** when we mapped the relationship::

    # mapped relationship, in the Breed class
    species = relationship("Species", backref=backref('breeds', order_by=name) )           
    
If we query for a species object, we will automatically have access to all the objects
that use this species, SQLAlchemy issues the SQL for the join for us. You might
think for a highly interconnected domain model that this would result in a lot of complex
queries being issued even for selecting one object. However, SQLAlchemy uses *lazy loading*,
meaning that the extra SQL for the join only gets generated and exectued if we actually
*use* species.breeds.

You'll also see in the above that we pass in an order_by argument to the backref 
function. This is used to generate an ORDER BY clause in the sql to load up the breeds
and means we can control the order of the breeds at species.breed.

In our example relationship, we do not need to specify how the join to connect these
classes is implemented. SQLAlchemy introspects on the table and is smart enough to 
see that there is a foreign key relationship between the two tables. On the other hand, 
if there more than one foreign key relationship between the same two tables, we would
have needed to specify the exact conditions for the join. We'll see this when we get
to self-referential mapping.

One source of confusion for those new to SQLAlchemy is where to map relationships.
We can actually map on either end, so long as we keep straight the backrefs.

For example, with our Species and Breed class, we could map the relationship
on either end. In the previous code we put the relationship in the Breed class,
but we could alternately have done the following ::

    class Breed(Base):
        __tablename__ = 'breed'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        species_id = Column(Integer, ForeignKey('species.id') ) 
        
        # we no longer need to add the breeds relationship as 
        # we get it from the backref on the Species class

    class Species(Base):
        __tablename__ = 'species'
        
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
    
        # specify the relation on the species end
        breeds = relationship("Breed", backref='species', order_by=Breed.name)

Note that in the above there are two other changes. We don't need the
backref *function*, and the order_by clause is an argument to the relationship
function not to the backref function. We also specify the order by with the
full *Breed.name* argument. 

It's important to understand that the two are functionally identical. In a 
complex model with many classes and many joins, sorting out which class needs
to be declared first can get tricky and knowing that you can map relationships 
on either end can be very handy.


Many-To-Many Relationships
--------------------------

When we map a many-to-many relationship, the mapping gets a bit trickier
as we have a joining table that is not attached to a specific model class,
our "pet_person" table. We need to create a table outside of our model classes
and then refer to it in the relationship declaration, like so:

    from sqlalchemy import Table, Text
    # our many-t0-many association table, in our model *before* Pet class 
    pet_person_table = Table('pet_person', Base.metadata,
        Column('pet_id', Integer, ForeignKey('pet.id'), nullable=False),
        Column('person_id', Integer, ForeignKey('person.id'), nullable=False)
    )

Note that we need to pass in our metadata object explicitly as this
is declared outside of a Base class. Now in the classes that are going
to use this table we need to explicitly refer to the association table
as SQLAlchemy is not going to be able to automatically determine the join
condition by introspecting. We do this with the "secondary" keyword argument ::

    class Pet(Base):
        __tablename__ = 'pet'
        
        id = Column(Integer, primary_key=True)
        name = Column(Text, nullable=False)
        # other attributes omitted ...
        
        # no foreign key here, it's in the many-to-many table        

        # mapped relationship, pet_person_table must already be in scope!
        people = relationship('Person', secondary=pet_person_table, backref='pets')

In this case we don't need anything in the Person class as the mapping
from that side is handled for us by the backref in the Pet class. Of course as
we've seen, we could also have done it the other way, with a relationship in the
Person class and backref for the Pet class. You may want to use comments in your
classes to indicate which ones have mapped relationship properties comming
from other classes ::

    class Person(Base):
        __tablename__ = 'person'
        
        id = Column(Integer, primary_key=True)
        name = Column(Text, nullable=False)
        
        # mapped relationship 'pets' from backref on Pet class 
        
Using the Many-to-Many relationship is just as easy as with One-To-Many, we
can remove and add items to the lists on each object, remembering that
the relationship is now bi-directional ::

    # add some pets to iain
    iain.pets.append( titchy )
    iain.pets.append( ginger )
    # ginger could be removed from iain's pets using the backref
    assert iain in ginger.people
    ginger.people.remove(iain)
    assert ginger not in iain.pets


Self-Referential Relationships - Adjacency List
-----------------------------------------------

Another common relationship in database designs is the Parent-Child relationship. This
can be implemented in the database using what's called and Adjancency List, where a 
table has a foreign key to itself to indicate a node's parent.  This is
really the same as a Many-To-One relationship, except that we need to be more explicit
about the join conditions for the backref to work properly by specifying the "remote side".
We need to specify the remote side or SQLAlchemy can't sort out the difference between the 
two directions automatically. For example, if we wanted to be able to track the parent-child
relationships of our pets ::

    class Pet(Base):
        __tablename__ = 'pet'
        
        id = Column(Integer, primary_key=True)
        name = Column(Text, nullable=False)
        
        # foreign key to self, must be nullable, as some pets will be the roots of our trees!
        parent_id = Column(Integer, ForeignKey('pet.id'), nullable=True ) 

        # Many-to-One relationship
        # NB: we must specify the remote side for the many-to-many backref to work
        children = relationship('Pet', backref=backref('parent', remote_side=[parent_id] ) )

In the above example, note one important difference from our previous One-To-Many example:
we have specified the *key* for the parent, but the *relationship* for the children. And in the
backref we tell SQLAlchemy that to determine the *parent*, the remote side of the join should
be the id column as we are joining from parent_id to id. Now we can make a hierarchy of objects
quite naturally ::

    # test pet parent child relationships
    root = Pet(name='Root')
    child_1 = Pet(name='Child 1', parent=root)
    child_2 = Pet(name='Child 2', parent=root)
    grandchild_1 = Pet(name='Grandchild 1', parent=child_1)
    grandchild_2 = Pet(name='Grandchild 2', parent=child_1)
   
    assert child_1 in root.children
    assert len(root.children) == 2
    assert len(root.children[0].children ) == 2
    assert grandchild_1 in root.children[0].children
    assert grandchild_1.parent.parent == root

    # and again we can change relationships by removing and adding to the childred lists
    # or writing to the parent attribute 
    for child in child_1.children:
        child_1.children.remove(child)
    assert grandchild_1.parent == None


While this kind of relationship can be tricky to get working when setting up your domain model,
you'll find it's extremely useful for any kind of hierarchal data, such as building a tree of
pulldown menus for a website.  It's easy to make mistakes with these
complex mapped relationships, so remember that there are excellent (though dense) examples in the SQLAlchemy
documentation for Relationship Configuration at http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html 


