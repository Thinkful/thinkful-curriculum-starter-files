In this assignment, we focus on *object relational mappers* (ORMs), which allow you to read from and write to your database *without* using raw SQL queries, which are cumbersome and hard to maintain.

Broadly speaking, the purpose of an ORM is to allow us to program more *naturally* in an object oriented language. When working with a relational database management system (RDBMS), our data is ultimately stored in tables, with individual elements stored as rows. Interconnected objects are difficult to represent this way, as the RDBMS has no inherent notion of a hierarchy or inheritance, while our Python code does. Thus representing even a moderately complex [object graph](http://en.wikipedia.org/wiki/Object_graph) can require many joins across many tables. This is cumbersome in SQL, and for a complex database, even simple updates can require long and error prone SQL queries.

This problem is sometimes called the *Object Relation Impedance Mismatch*, which is basically just a fancy way of saying that it can be really difficult and convoluted to represent otherwise simple and intuitive Python objects in relational databases, and conversely, it can be challenging to represent complex relational database data in terms of simple Python objects. ORM's are designed to solve this problem by allowing us to work with objects in our application code, leaving the generation and execution of the actual SQL to the ORM.

# Raw SQL vs. ORM

To see the advantages of working with an ORM over raw SQL, let's return to our pet database example. Imagine we we want to get our data persistence layer to reflect the fact that Iain is leaving the country and must give all his dogs to Ben. In SQL, we would need to issue some complex queries to manage our many-to-many relationship of pets to people:

```sql
INSERT DEMO SQL CODE FOR THIS HERE
```

With an ORM, we can use code that reads like how we think about the problem. Programmers say that the code is *reflective of the problem domain*, we are working with objects that match real world objects in our **domain model**. This is preferable to working with the SQL, which is reflective of the *implementation*, tables and rows of simple data types. 

```python
# retreive Iain and Ben as objects, using their db IDs
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
```

This is a lot more readable than working directly with psycopg or SQL.
To update Ben's pets, we remove a pet from the list `iain.pets` and add it
`ben.pets`; the ORM takes care of sorting out the SQL. To find out if a pet is a dog, we check `iain.pets[ pet_index ].breed.species.name`. The required joins are all executed behind the scenes; this one variable represents the work of four joins! 

What's more, this decouples our *business logic* or *application logic* from the database implementation. If our table names, column names, or table structures change, none of the code in this example would need to be changed. If we changed our table structure so that pets could only have one person, removing the many-to-many table and replacing it with a one-to-many relation, we would not need to change anything in the example, Ben's pets can still be accessed and mutated as a list at `ben.pets`, regardless of how this relationship is represented at the database layer. As you can imagine, this is a huge maintability benefit in complex projects.

# Using Properties to Separate Data from Presentation

[ rewrite this so it very briefly introducees properties!]

In combination with Python *properties*, ORMs give us an effective boundary between business logic, database rules, and presentation logic. Continuing with our pets database example, let's imagine that we want to write some rules that prevent certain kinds of updates, and to do this we need logic that is too complex to reside in SQL. Let's assume we also want to add these constraints an already running system, and preferably not have to change any of our existing application code. 

More specifically, our requirements are that that a person *must* always have a full 10 digits for their phone number, and it will always be stored as a 10 digit string without hyphens or spaces, **but** will (for now) be displayed using hyphens. We don't want to change the fact that we are already reading or updating a person's phone number using the **Person.phone** member variable, as we already have code doing this. This is an example of wanting to preserve the **public interface** to our domain model. Here's our starting point:

```python
example of pre-property code
```

By telling SQLAlchemy that we will map a *private* Python property, **Person._phone**  to the 'phone' field in the 'person' table, we can
add code that executes when the *public* property **Person.phone** is accessed,
and have this code prevent a bad update and store only digits. 

```python
class Person(base):
    # boilerplate ommitted here -- we'll cover that later        
    
    # phone number accessing property, reading Person.phone will call this.
    # the property just deals with the presentation of the underlying, private
    # data variable, _phone
    @property
    def phone(self):
        """return phone number formatted with hyphens"""
        # get the phone number from the database, mapped to private self._phone
        num = self._phone
        # return a formatted version using hyphens
        return "%s-%s-%s" % (num[0:3], num[3:6], num[6:10])

    # phone number writing property, writing to public Person.phone calls this 
    @phone.setter 
    def phone(self, value):
        """store only numeric digits, raise exception on wrong number length"""
        # strip out hyphens and spaces
        number = value.strip(' -')
        # check length, raise exception if bad
        if len(number) != 10:
            raise BadPhoneNumberException("Phone number not 10 digits long")
        else:
            # write the value to the property that automatically goes to DB
            self._phone = numbner
```

With the above definition of the Person class, we now can use the person object
very naturally, and other parts of our program that are *using* the Person.phone property do not need to be changed.

```python
# get some input values in a dict, will have a key 'phone' with some input
input_dict = get_input_values_somehow()

# write the value to our person
# Person class takes care of storing only digits, and throwing exception
# if the input is bad  
try:
    ben.phone = input_dict['phone']
except BadPhoneNumberException, e:
    log.error('Error: bad phone number for person %i. Exception: %s' % (
      ben.id, e))
```

Even more succintly, this allows us to use input dictionaries with keys
corresponding to property names on our objects so we can update many attributes
of an object in one loop. Here's an example:

```python
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
```

The code above has a number of good characteristics: 

*   Our application code is readable and small; it is obvious what we are doing.
*   The way we deal with people is consistent, we always write and read the
same properties, no matter how we change the database or the validation and conversion methods.
*   Our validation and conversion code lives in a sensible place, on the Person
class, instead of sprinkled throughout our application in every place that we update people.
*   We can change any of our layers independently of each other: application logic, validation & conversion, and database persistence.

# ORMs and Unit Testing

Using an ORM makes writing unit tests for our application code much easier. Because we are using plain old objects in our business logic and accessing fields through simple attributes of the objects, we have the option of substituting in other objects in a test scenario, so long as our substitute objects fulfill the same public interface. This is practice is called [**mocking**](http://en.wikipedia.org/wiki/Mock_object) and the objects are called **mock objects**. Our application code can include functions and methods that receive objects as paramaters, working with and on those objects, but ignorant of how the objects themselves work. For example, this method transfers pets from one person to another:

```python
def transfer_pets(person_from, person_to):
    """transfer pets, but only for allowed species"""
    for pet in person_from.pets:
        if pet.breed.species in person_to.allowed_species:
            person_from.pets.remove(pet)
            person_to.pets.append(pet)
# the call to session.commit happen elsewhere
```

In the above method, there is no coupling of the function to *how* we store a 
pet-person relationship, we just know that it is *accessed* through a list at Person.pets. For that matter, the function doesn't even know that these are database backed objects, it just knows that we can get pet objects from person.pet. Thus if we want to unit test this method without having to connect to a database during the tests, we can write tests that call the function with mock objects, so long as the mock objects behave like the interface they mock. This means the tests run faster and require less database related setup and tear down. If we were using raw SQL queries in our method, this would not be possible. On very large projects with hundreds of tests, this can be a very significant speed up.

# ORM Setup

Hopefully by now you can see that for a project of any complexity, using a good ORM along with Python properties is a huge improvement over hand writing SQL. Of course, this begs the question, "How does updating an object magically make the SQL happen?"

In the examples above, we are only showing code that is *using* the ORM, but have skipped the code that *sets up* our ORM and our SQLAlchemy **domain model**, the collection of classes modelling the objects stored in our database. We need a certain amount of housekeeping code to set up a domain model so  SQLAlchemy knows what to do when we update our objects, and we need some housekeeping that makes SQLAlchemy talk to the database, initializing the engine and connections, etc. Compared to our simple psycopg2 examples in the last lesson, this *boilerplate*, as programmers call it for SQLAlchemy, is a fair bit of extra code. 

However, we create the boilerplate only once, no matter how complex our application gets, and every *use* of the objects is simpler to read and maintain, more flexible, and less error prone. For a very simple database script that only selects a few records and updates them, the overhead of setting up an SQLAlchemy domain model and initializing the engine may not be worthwhile. For a larger project however, this becomes a very powerful use of the Don't-Repeat-Yourself principle: we only concern ourselves with *how* we map to SQL once, and after that we can work very easily with plain old objects.