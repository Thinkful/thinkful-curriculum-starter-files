Using PostGreSQL
================ 

We've now got a pretty good handle on the basics of SQL, and we've build a database
in sqlite and interacted with it over the sqlite3 terminal. In this lesson we'll 
be switching over to using the PostGreSQL RDBMS and learn how to use our database within
a Python application. The PostgreSQL RDBMS used to be called just Postgres and you'll
see that term used as a casual name for PostgreSQL frequently. (However, when 
searching for documentation you should use the full term so you don't find only
older documentation pages!)

To begin with, let's look at the differences between SQLite and PostGreSQL and
get our postgres database. 

Old
# Using the database that you finished with in the last lesson, creat an SQL file
# by dumping the SQLite database. Then use psql terminal to create a new postgres
# database from the same contents. Verify that your new database is working by
# connecting to it with psql in the console and issuing some queries. We want
# to make sure that we can be looking at the state of our database as our Python 
# script executes. You may want to run psql in one tab of a terminal operation
# while running the Python script in another.
# (XXX: Ben is this ok??)


Setup
-----
- here thar be a magical black box to get them up and running on postgres.
- we now have:
  - a postgres user they can switch to
  - created a database named 'pets' that they can connect to  
  - a running PSQL terminal 
- NB: for now on I'm dodging the permissions issue and assuming everything is
being done as the postgres user 

Differences
-----------

PostGreSQL is an industrial strength open source RDBMS used for mission critical
high bandwidth applications all over the world. Postgres provides built in support
for explicit constraints by default, whereas in SQLite, one has to enable 
constraints. This makes SQLite idea for first learning, or for embedding for
single user applications, but for real world multi-user situations you are 
well advised to set up constraints as well as you can to ensure database integrity.

This means that we'll have some additional SQL for generating our tables. We're
going to revisit our pet database construction now to add these constraints.
We'll be adding foreign key constraints forcing our foreign keys to have valid
values. We'll also be enforcing uniqueness on columns that shouldn't have
duplicate values, and we'll be using Postgres's **sequence*** ability to
have Postgres automatically create sequential integer primary keys for us.


Primary Keys and Sequences
--------------------------
When using a database in a multi-user context, it's generally a good idea to
leave the generation of integer primary keys (our 'id' columns) up to the 
database. We want to insert records without specifying the key, like so ::

    insert into breed (name) values ('Persian'),('Tabby'),('Mixed');

Note we are leaving out the id column from both sides of our query. There
are a couple of ways of making this work properly in Postgrest. The one
we're going to use is the sequence command. Our Species table creation will
now look like this ::

    CREATE SEQUENCE species_id_seq;
    create table species (
        id integer primary key default nextval('species_id_seq'),
        name text not null
        );
    ALTER SEQUENCE species_id_seq OWNED BY species.id;

The first line creates a a new *sequence* and names it species_id_seq.
The sequence is a stand-alone entity that creates sequential values.
In the definition of the 'id' column, we see the addition of 
"default nextval('species_id_seq')". This means that if no value is 
given, postgres will automatically insert the next integer value from
the sequence for us. Finally, the last statement means that if the
species table is dropped, this sequence will be dropped as well. 

An important side effect of this is that we should not mix explicit
generation of id columns with use of the sequence, or the sequence will
get out of sequence. I.E: if we create a record, generating the id
ourselves, and then subsequently create a record without specifiying 
the id, we'll get an error as the sequence will try to create a duplicate
id. There are advanced techniques to get around this issue, but
we'll use the suggested practise of *always* letting the RDBMS determine
our primary keys.


Foreign Key Constraints
-----------------------
Next we'll look at our Breed table, which has a foreign key to the
species table id :: 

    CREATE SEQUENCE breed_id_seq;
    create table breed (
        id integer not null primary key default nextval('breed_id_seq'),
        name text not null,
        species_id integer references species(id)
        );
    ALTER SEQUENCE breed_id_seq OWNED BY breed.id;

In this table we see the addition to the species_id column of 
"references species(id)". This addition will enforce the constraint
that species_id can *only* hold a valid id value from the species table.
This has some strict side effects: We can't delete an entry from the species
table as along as there is still an entry in the breed table that references
the entry we're trying to delete. The RDBMS won't let us and will 
give us back an error message. If we want to change our constraint
rules so that we *can* delete a species and all the breeds associated
with it are also deleted, we can add cascading rules in the database
definition ::

    species_id integer references species(id) ON DELETE CASCADE

Alternately we can add a constraint to instead set the orphans
to have null values for the foreign key ::

    species_id integer references species(id) ON DELETE NULL

Further details on constraint options are in the official
PostgreSQL docs for Create Table: 
http://www.postgresql.org/docs/9.0/static/sql-createtable.html


Many-To-Many Tables
-------------------
For Many-To-Many tables, we'll use the foreign key definitions
we've just discussed, and also add a primary key constraint
to let PostgreSQL know that the combination of the two foreign
keys is our primary key and must be unique ::

    create table pet_person (
        pet_id integer references pet(id),
        person_id integer references person(id),
        primary key (pet_id, person_id)
    );


Uniqueness
----------
PostgreSQL will automatically enforce uniqueness for anything
we declare as a primary key. We can also enforce uniqueness
for additional columns, for example perhaps we want to 
enforce that there be no duplicate first and last names
in our person table, and no duplicate email addresses ::

    create table person (
        id integer primary key default nextval('person_id_seq'),
        first_name text not null,
        last_name text not null,
        email text,
        
        unique( first_name, last_name),
        unique( email )
    );


Inserting Records with Foreign Keys
-----------------------------------

One wrinkle we have now that we've defined our tables with
foreign key references, is that we can no longer do this ::

    insert into species (id, name) values (1, 'Cat');

    insert into breed (id, name, species_id) values
        (1, 'Persian', 1);

Because we're leaving key generation up the RDMBS, we now
use a subquery for inserting our foreign keys ::

    insert into species (name) values ('Cat');

    insert into breed (name, species_id) values 
        ('Persian', (select id from species where name='Cat') );


Next Steps
----------
This should cover us for getting our database converted over
to PostgreSQL. You should download the starter file for
creating our PostgreSQL verions of our pets database and
get it loaded with pqsl. We can do this by redirecting the SQL file
into pqsl ::

    psql -d pets < pets_postgresql.sql

Before proceeding to the next assignment, make sure your
new database is working by connecting to with PSQL and
issuing some queries. 

Like SQLite, PostgreSQL has its own specific commands that
are not terminated with a semicolon. In PostgreSQL, these
start with a \. Here are a few you'll want while using psql

    \dt
        list all tables
    \d+
        list all tables and sequences
    \d+ pet 
        describe the pet table in detail
    \q
        quit
    \?      
        show help
     

(TODO: have them download the postgres starter file)
Download the file pets_postgresql.sql or whatever it will
be called.
