Lesson 4 - Advanced Querying
============================

In this assignment we'll recap the querying techniques we've already demonstrated and
introduce more powerful filtering and joining options.

One important point to keep in mind is that when we use a session to query the database,
we are querying both the session and the database. If we've created a new object in this
session but haven't committed to the database yet, any queries on the current session will
retrieve the pending object, even though it does not yet have an ID. 

Query objects are *generative*. All the operations on a query object *except* terminal 
operations return new query objects. This way we can build up a query bit by bit. We terminate
it with an operation that does something like count, retrieve, or delete the results of 
the query. Our most basic query object gets everything from a model class ::

    species_query = db_session.query(Species)
    # now we have a query object and can use it a few ways
    
    # get a list of all species items
    species_query.all()

    # or get just the first one
    species_query.first()

    # or just count them
    species_query.count()

    # we can peek at the SQL
    print "%s" % query.statement
    # prints: 'SELECT species.id, species.name \nFROM species'
   
    # refine our query
    from sqlalchemy import desc
    species_query = species_query.order_by( desc(Species.name) )
    
    # get all the items, now ordered by name descending
    species_query.all()


SQLAlchemy has methods for all the SQL operations we might want to add to a query:
filtering, ordering, limiting, offsetting, subquerying and many more. We also 
get a variety of terminal methods that return lists, single objects, or raise exceptions. 


Basic Get
---------

Our most basic query is one we've seen already, the get by primary key query. This is
used when we have the database ID and is common in web applications where the ID
may be in the URL of a page ::

    # hypothetical ID retrieval
    species_id = get_id_from_url()
    species_item = db_session.query(Species).get( species_id ) 
    # species_item is not either a Species object or None

This query will return the object, or a None value.  
Logically, we can see that query.get can not normally fetch a pending item as it needs the ID.
However, if we had explictly passed in the primary key on creation, we would also be able
to get an item from the session before it was persisted to the database ::

    # create a species, passing in the id instead of letting SQLA determine it for us
    parrot = Species(id=4, name="Parrot")
    dbs.add(parrot)
    
    # we haven't committed, parrot is not in the database yet!
    fetched_parrot = dbs.query(Species).get(4)
    
    # we got back a reference to parrot
    assert fetched_parrot
    
    # now change our original parrot
    parrot.name == 'The Majestic Parrot'

    # has fetched_parrot changed?
    assert fetched_parrot.name == "The Majestic Parrot"

    # YES! SQLAlchemy knows that they should the *same* object
    assert fetched_parrot is parrot

As you can see in the code comments, if we do this we wind up with a new reference
to the *same* object. SQLAlchemy's Identity Map can see that we are talking about the
same database object and will ensure that all references work properly. 

Exercises:
----------
1) In your script, create some items, commit, and then get them with a new session using
  their primary key.
2) Get back a new reference to the same record, and change it. Check that the change has
  also happened on your original object.


Filtering
---------

The next most likely operation is to filter our query. We can do this with either a 
**filter** clause or a **filter_by** clause. When we use filter_by, we pass in keyword
arguments as simple string keys and python values. The retrieved object must match
any keys passed in. 

    # pass in some keyword args
    query(Species).filter_by( name='Parrot', id=4).all()

We can use filter_by along with Python's dictionary expansion operator to filter
on a dictionary very succinctly :: 

    # maybe we get a dict of search terms somehow
    filter_dict = dict( id=4, name='Parrot')
    db_session.query(Species).filter_by( **filter_dict ).all()

Filtering is again generative so this could also be built up bit by bit:

    query = db_session.query(Species).filter_by( name='Parrot' )
    query = query.filter_by( id=4 )
    parrot_list = query.all()

We use the **filter** operation to filter with more powerful options than simple
keyword matching. Filter accepts expressions in the SQLAlchemy expression language.
We can filter on complex types, date ranges, add in logical AND and OR options, etc.
When we filter on an SQAlchemy expression, we use an attribute of the model *class*.
Also, note that these are *expressions*, so we are using == instead of = ::

    people = db.session.query(Person).filter( Person.city == "New York" ).all()
    # we can pass in multiple expressions separated by commas
    people = db.session.query(Person).filter( 
        Person.city=="New York", Person.state=="NY" ).all()

SQLAlchemy has a number of helper functions for common operations, such as AND and OR ::

    # NB: and_ and or_ are so named to avoid conflicts with Python's reserved words
    from sqlalchemy import and_, or_

    # find a person named either Ben or Iain
    people = db.session.query(Person).filter(
      or_( Person.name=="Ben", Person.name=="Iain") ).all()

Other operations are available as operators on the mapped properties of the class. 
Here we can do string matching using a 'like' clause ::

    # get any species with the letter a in the name 
    db.session.query(Species).filter( Species.name.like( '%a%' ) ).all()

We can also check for list membership (or lack thereof)::

    # get people named Ben, Iain, or John
    possible_names = ['Ben', 'Iain', 'John']
    db_session.query(Person).filter( Person.name.in_( possible_names ) ).all()
    # or not in, using the ~ symbol to negate the operation
    db_session.query(Person).filter( ~Person.name.in_( possible_names ) ).all()

For futher possibilities, the SQLAlchemy ORM Tutorial has a comprehensive section
on filtering. http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#common-filter-operators

We also have a few different options for how we get the results of our query.
You've seen us using query.all(), but we can also use query.one(), query.first() 
and query.scalar() ::

    query = db_session.query(Person).filter( Person.first_name == "Iain")
    
    # get all the Iains, or an empty list if none
    iain_list query.all()
    
    # get one Iain, raising an exception if there is not exactly one 
    from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound 
    try:
        iain = query.one()
    except NoResultFound, e:
        log.info("Error: no result found")
        iain = None
    except MultipleResultsFound, e:
        log.info("Error: multiple Iains were found")
        iain = None 
    
    # get the first or only Iain, or None  
    # unlike all, no results returns None instead of an empty list 
    iain = query.first()
   
    # scalar asks for either one item, or None, but an exception on too many
    # this is like query.one(), except a None is permitted
    try:
        iain = query.scalar()
        # iain could be None here...
    except MultipleResultsFound, e:
        # but too many Iains raises an exception
        log.info("Error: multiple Iains were found")
         

Another common operation we might need is the ability to limit our retrieval to certain
items within the master list. For large databases, this is much more memory 
efficent than loading up a giant list and slicing in Python ::

    # maybe we have 1000000 pets in the db!
    # we want the second page of pets, displaying 50 per page
    
    # bad: pet_list is huge and is loaded before our slice happens!
    pet_to_show = db_session.query(Pet).all()[ 50:100 ]

    # good: pass of the work to the db and only load 50 pets
    pets_to_show = db_session.query(Pet).offset(50).limit(50).all()

This is a good way to make a paginated view, a common need in making database
backed websites ::
    
    page_num = get_page_from_url()
    items_per_page = get_page_option()
    
    items = query.offset( items_per_page * (page_num - 1) ).limit( items_per_page).all() 

XXX: add in order_by yo

Exercises:
----------

1) Using the debugger, query for items using filter_by. Pass in a dictionary as well.

2) Do the same with filter. Try some searches using the following:
   * and_
   * or_
   * like
   
3) Read over the querying options in the SQLAlchemy documentation.


Joins
----- 
Left off here


