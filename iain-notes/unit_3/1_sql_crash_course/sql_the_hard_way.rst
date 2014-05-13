Lesson 2: SQL The Hard Way
==========================
(Status: finished draft with exercises, Apr 29, 2014

To learn SQL, we're going to work through the online book "SQL The Hard Way", by Zed Shaw,
the author of "Learn Python the Hard Way", along with some companion lessons and exercises of our own.
The book is located at http://sql.learncodethehardway.org/book/
You'll notice that this is an incomplete book, however it's very well writtten we'll use it up
to Exercise 15. Each Exercise is fairly short and includes examples using an SQLite database. 
You should work along with the examples and make sure you get everything working on your
own SQLite database.  We'll be providing our own assignments for each exercise that you should do
on your database in addition to the examples. There are also Extra Credit suggestions in the
book that are not necessary, you can try if you'd like, but you should use an alternate copy 
of your database for those so that your main pets database stays in sync with our lesson plan. 
We'll be continuing to use the pets database in the next lessons as well.


Book Ex 0 to 4,  Assignment 1 - extending our schema
-----------------------------------------------------
Complete Exercises 0 through 4 and then come back here, don't worry about the extra credit material
for now, though you can go back to it later if you'd like.

At this point we have a database with three tables, one containing people, one containing
pets, and one containing relationships between pets and people. We call this a Many-To-Many
relationship: more than one person can have the same pet, and a person can have more than one 
pet. Our person_pet table captures this relationship. We can say that it models an "association"
between people and pets. This association table contains references to both the pet and person 
table. In the person_pet table, the column 'person_id' is what we call a Foreign Key; it contains
the integer value of the 'id' field of the Person table, which is the Person table's Primary Key.
It should only ever contain a valid primary key from the person table, any other integer would
be considered invalid data. It thus acts as a connector between the tables, and the same holds
true for the 'pet_id' column; it references the id column in the pet table. You can see that
this is a symetrical relationship, it's the same kind of relationship looked at from either
end. You may read of these as "bi-directional".

A One-To-Many or Many-To-One relationship on the other hand is not bi-directional. Let's take the
example of a Breed: a pet can only be one breed of animal (we'll ignore mixed breeds for now!). But
we could have many pets of one breed, thus a breed could 'have' many pets. If we add a Breed table,
we can put a foreign key in the pet table that refers to the primary key of the Breed table,
replacing the text column for breed that we have so far from the book's database:

    create table breed (
        id int, 
        name text,
        species text
    );
    create table pet (
        id int, 
        name text, 
        age integer,
        dead integer,
        breed_id integer
    );

Now if we insert data we can capture the One-To-Many relationship between Pets and Breeds:

    insert into breed (id, name) values (1, "Tabby"), (2, "Siamese"), (3, "Persian");
    insert into pet (id, name, age, dead, breed) values (1, "Titchy", 17, 1, 1);
    insert into pet (id, name, age, dead, breed) values (2, "Tiger", 6, 0, 3);

We now have two cats in our table with identical values in the column 'breed_id', instead
of having two identical text strings for "Tabby" in the pet table. This helps us avoid
**duplication of data** in our tables, and is part of a process called **Normalization** in 
which duplicated data is refactored out into multiple tables using foreign key relationships.

Why is this important? Let's imagine that we
are running a pet shelter database, and we have a facility for potential adopters to
search for pets by breed. Facility staff enter new pets as they arrive for adoption.
What if someone makes a typing mistake and spells "Tabby" incorrectly? We have two
tabby cats, but if our program searches for the string "Tabby", it's only going to find
one entry. We have a case where our data integrity has been broken: our database
doesn't *seem* to have any errors, but it's modelling an incorrect representation of
reality: we have two cats of the same breed and only one will show up and get adopted,
a critcal error for our application!

Another potential problem arising from duplication of data comes when updating. Let's imagine
our staff member didn't know how to spell "Mayne Coon" and entered it incorrectly.
In our naive implementation with a text column for breed, all the entries that used
the old spelling need to be individually updated, and it's easily possible that the query
to find them might miss some, and only some of our rows that should be identical get
updated. This is called an "Update Anomaly". In our normalized
schema, only one entry in one table needs to be changed, and we greatly reduce the chance
of update anomalies.

This process of normalizing can be extended across many tables. The astute reader
will notice that we have the same issue in the breed table: a breed can only be of
one species but we're capturing species as a text field.

Before proceeding to the next set of exercises, make a copy of your database
and do the following with your new copy (it's a good idea to keep many copies
as SQL dumps to make it easier to revert):


Part 1 Exercises:
-----------------

- Add a species table
- Add a breed table, with a foreign key to the species table
- Redo your pet table to use a foreign key to the breed table
- Add a phone number and email address to the person table
- Add a boolean column to the pet table for 'adopted'.
- Insert some values for species, breed, pets and people.
- Insert some values into the person_pet table to capture relationships.


Part 2 - Book Ex 5 to 11 - Selecting, Deleting, Updating
--------------------------------------------------------

Read the Book exercises 5 to 11, and then come back here. Again, don't worry about
the Extra Credit if you don't want to, we'll be providing lots to do right here.

At this point, we have a database with several relationships, and for 
certain operations we need to join across several tables, a common scenario in
a real world database. You can now select, delete, and update using joins and
subqueries, so for our assignment, we'll practise making some selects and updates 
using joins and subqueries:

Part 2 Exercises:
-----------------
- Select all the cats.
- Update all cats to set adopted to False (in 1 query)
- Select all the pets belonging to a specific person
- Update all the cats belonging to a specific person to set adopted to True.


Part 3 - Foreign Key Constraints and the Cascade
------------------------------------------------
Read the book exercises 12, 14, and 15 and come back here 
(13 is an assignment that we'll be replacing with our own so you can skip it).
At this point you've got a pretty good grasp of the fundamentals of database
design and some of the issues we need to be aware of. You're also aware of
transactions, and the basics of normalization. 

Now, in a real world database for a critical operation, such as listing the pets
available for adoption, normalization raises some new issues:

 * What happens to the pet_person table if we delete a person?
 * What happens to our pet and breed tables if we delete a breed?
 * What *should* happen to our pet table if we delete a breed that has pets? Should this even be possible?
 * What happens if we enter garbage integer data into any of our foreign key columns?
 
The issues are important to consider in designing a database. At present, if we
delete a pet who had one or more people, we'll have some nonsensical entries hanging around
in our person_pet association table.
Worse, if we delete a species, we'll have invalid entries in the breed table, where we'll
have species_id columns referencing non-existing Species entries. These problems are called
data consistency problems. They put our database in such a state that it represents a nonsensical
real world state. This sort of problem can be especially difficult to debug as our 
program may not have any *programming errors* per se, but the outcomes will be incorrect. 

To solve these sorts of  issues, database systems allow us to specify what are called
**Foreign Key Constraints**.
We can tell the database that a foreign key column *must* refer to a valid related entry, 
or that certain operations should not be permitted, or that certain operations should automatically
trigger other operations. For example, we
could specify a foreign key constraint that says that we can not delete a species entry
if any breeds are still referencing it. Or we could alternately specify that deleting a species
entry automatically deletes all breeds referring to it. Or that breeds referring to it should have
their foreign keys changed to Null. 

These sort of rules are referred to as "The Cascade", we specify
how changes should *cascade* to their related dependent entries in other tables. And to do so, we need to 
spend some time thinking about what is logical for our specific data model. For example, sometimes
it makes sense that a foreign key could be null, and other times that is obviously a mistake. If 
we add a pet shelter table to our database, and add a relationship between the pet table and the shelter 
table, we can see that it makes sense that:

  - a shelter can have many pets
  - a pet only comes from one shelter
  - but a pet may also not come from any shelter, thus null is a possible valid value

The syntax for specifying foreing key constraints in SQL can be a bit involved, and enabling
foreign key constraints in sqlite requires some extra configuration, so we will not get into
the details at this point. We will be coming back to the cascade in further detail in subsequent
lessons however. And even if we don't specify constraints at this time, it's important to 
understand the ramifications of normalization when designing any system using a relational data model. 

Part 3 Exercises
----------------
- go to https://www.sqlite.org/foreignkeys.html and read Section 1, "Introduction to Foreign Key Constraints",
  and section 4.3 "ON DELETE and ON UPDATE Actions" 
- add a shelter table, with values for name, address, phone number, website
- update our pet table without recreating it to include a foreing key reference to the shelter
  that a pet is at or is from
- what do you think *should* happen (or be prevented) in we attempt the following:
    - deleting a species?
    - deleting a shelter? 
    - deleting a person?
- how is the foreign key relationship for pet to pet shelter different than from pet to breed? What
  would we need to specify to make this clear?


