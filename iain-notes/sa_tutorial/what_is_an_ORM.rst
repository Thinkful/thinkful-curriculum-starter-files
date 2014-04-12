What is an ORM, and why use one?
================================

Broadly speaking, the purpose of an ORM is to allow us to program more *naturally* in
an object oriented languauge. When working with a RDBMS (relational database management
system), ultimately data is always stored in tables, with elements as rows. Interconnected
objects are difficult to represent easily this way, as the RDBMS has no inherent notion
of a hierarchy or of inheritance. Thus representing even a moderately complex object graph can require many
joins across many tables. This is cumbersome to deal with in SQL,
and even simple updates can require long and error prone SQL queries.
This issue is called sometimes called the Object Relation Impedance Mismatch: that which
makes sense and is simple in terms of Python objects is complex and difficult to manage in  SQL and
vice versa. An ORM bridges this divide by allowing us to work with objects directly, leaving the
generation of the actual SQL to update them to the ORM.

Using our pet database, let's say Iain is leaving the
country and must give all his dogs to Ben. In SQL, we would need either one very complex SQL query
and subqueries, or a loop with several queries to accomplish this. With an ORM, we can use code 
that reads the same way we are thinking about the problem. Programmers say that the code
is *reflective of the problem domain* (objects representing real world things) instead of the 
implementation details (SQL referring to tables and rows) ::

    # get Iain and Ben, using their db IDs
    iain = session.query(Person).get(4)
    ben = session.query(Person).get(5)
    # iterate through Iain's pets
    for pet in iain.pets:
        # if the pet is a dog, give it to Ben
        if pet.breed.species.name == 'Dog':
            iain.pets.remove(pet)
            ben.pets.append(pet)
    # commit our transaction, this flushes ALL the SQL for all the above
    # in one fell swoop
    session.commit()        

As you can see, this is vastly more readable than working directly with psycopg and SQL.
To update Ben's pets, we simply remove a pet from the list **iain.pets** and add it
**ben.pets**; the ORM takes care of sorting out the needed SQL. To find out if one of Iain's pets is a dog,
we can just look at **iain.pets[ pet_index ].breed.species.name**. The joins required for this
are all executed for us behind the scenes; this one variable represents the work of four joins! 

What's more, this *business logic* or *application logic* code is decoupled from the database implementation.
If our table names or table structures change, none of the code in this example needs to be changed.
For example, if we changed our table structure so that pets only have one person, removing
the many-to-many table and replacing with a one-to-many relation, we would not need to change *anything* 
in the example above, Ben's pets can still be accessed and mutated as a list at **ben.pets**.
This is a huge maintability benefit in large projects with complex databases.

A third less obvious advantage of this pattern is that in combination with Python *properties*,
this gives us a very effective *boundary zone*.  Let's imagine we also want to add some business
level rules, distinct from database level rules. We want to prevent certain kinds
of updates, with logic that is too complex to express as a database constraint. But we want
to add these constraints to an already running system with minimal changes. For example,
let's say that a person *must* always have a full 10 digits for their phone number, and it will
always be stored as a 10 digit string without hyphens or spaces, but will (for now) be displayed
consistently with hyphens. However, we don't want to change the fact that we are already reading or update
a person by just using the  **Person.phone** member variable, as we already have a lot of code working that way.
By telling SQLAlchemy that we will actually map a private Python property, **Person._phone** 
to the database rows for **person.phone**, we can
add executable logic that runs when Python code tries to update the public property **Person.phone**,
and have this code preventing a bad update and storing only the digits. And we can do so in a manner
that ensures that changing our validation rules later is a snap. ::

    class Person(base):
        ... boilerplate ommitted here that will come later ...        
        
        # phone number accessing property, reading Person.phone will call this
        @property
        def phone(self):
            "return phone number formatted with hyphens"
            # get the phone number from the database, mapped to self._phone
            num = self._phone
            # return a formatted version using hyphens
            return "%s-%s-%s" % (num[0:3], num[3:6], num[6:10])

        # phone number writing property, writing to Person.phone calls this 
        @phone.setter 
        def phone(self, value):
            "store only numeric digits, raise exception on wrong number length"
            # strip out hyphens and spaces
            number = value.strip(' -')
            # check length, raise exception if bad
            if len(number) != 10:
                raise BadPhoneNumberException("Phone number not 10 digits long")
            else:
                # write the value to the property that automatically goes to DB
                self._phone = numbner


With the above definition of the Person class, we now can use the person object
very naturally ::

    # get some input values in a dict, will have a key 'phone' with some input
    input_dict = get_input_values_somehow()
    
    # write the value to our person
    # Person class takes care of storing only digits, and throwing exception
    # if the input is bad  
    try:
        ben.phone = input_dict['phone']
    except BadPhoneNumberException, e:
        log.error("Error: bad phone number for person %i. Exception: %s" % (
          ben.id, e)


Even more succintly, this allows us to use large input dictionaries where the keys
correspond to property names on our target objects and update many values on 
a person in one loop:
    
    # get a dictionay of input values to use for an update 
    input_dict = get_input_values_somehow()
    # IE {'phone':'123-456-7890', 'email':'iain@iainduncan.com', 'first_name':'iain'}
    
    # get the person we want to update
    iain = session.query.get(4)

    # write all the values to our person, allowing the properties on the 
    # Person class to deal with any validation or conversion issues
    for key, value in input_dict.items():
        # if the person object has a property matching this key, update it
        if hasattr(iain, key):
            setattr(iain, key, value)    

    # commit, generating the SQL and running the transaction
    session.commit()
   

In the above example, we have accomplished a number of Very Good Things for 
larger projects:

    * our application code is readable and small, it is obvious what we are doing
    * the way we deal with people is consistent, we always write and read the
      same properties, no matter how we change the DB or the validation & conversion methods
    * our validation & conversion code lives in a sensible place, on the Person
      class, instead of sprinkled throughout our application wherever we update people
    * we can change any of our layers independently of each other: application logic, 
      validation & conversion, and database persistence


EDIT THE Below, not finished.

Lastly, using an ORM makes writing unit tests much easier as we can substitute **Mock**
objects for our SQLAlchemy backed objects. Our application code can have functions and methods
that receive objects and do things to objects, with these methods maintaining ignorance
of how the objects work. For example, this method transfers pets from one person
to another :: 
   
     def transfer_pets(person_from, person_to):
        "transfer pets, but only for allowed species"
        for pet in person_from.pets:
            if pet.breed.species in person_to.allowed_species:
                person_from.pets.remove(pet)
                person_to.pets.append(pet)
        # the call to session.commit happen elsewhere

In the above method, there is no coupling of the function to *how* we store a 
pet-person relationship, we just know that it is *accessed* through a list at Person.pets.
Thus if we want to unit test this method without having to to use a real
database, we can call it with Mock objects, so long as they fullfill how we expect
to work with them. All the mock objects need to do 
is properly implement the lists and member variables we are expecting to work with.
Our method doesn't care *how* we get pet.breed.species or what happens with the 
.pets list. This mean run faster and require less overhead
by having them fake out the database. If we were using raw SQL queries in our
method, this would not be possible. On very large projects with hundreds of tests,
this can be enormously beneficial.    


Hopefully by now you can see that for a project of any complexity, using a good ORM
with Python properties is a huge improvement over hand writing SQL. Of course, this
begs the question, "how does updating an object magically make the SQL happen?"

In the examples above, we are only showing code that is *using* the ORM, but have 
skipped the code that *sets up* our ORM. We need a certain amount of housekeeping 
code to setup a data model such that SQLAlchemy knows what to do when we update our
objects, and we need some housekeeping that makes SQLAlchemy go (initializing the
engine and connections, etc). Compared to our simple psycopg2 examples in the last
lesson, this *boilerplate* (as programmers call it) is a fair bit of overhead. 
However, the boilerplate happens only once, no matter how complex our application gets,
and every *use* of the objects is simpler to read and maintain, more flexible, and 
less error prone. For a very simple database script that only selects a few things 
and updates them, the overhead of setting up an SQLAlchemy data model and initializing
the engine may not be worth the savings. For a larger project however, this becomes
a very powerful use of the Don't-Repeat-Yourself principle: we only concern ourselves
with *how* we map to SQL once, and after that we can work very easily with plain old objects.


