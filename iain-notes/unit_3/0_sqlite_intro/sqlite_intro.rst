Introduction to SQLite - Lesson 1
==================================

In this first lesson, we'll get SQLite up and running and connect to it so we can
use it while we work through the online book "Learn SQL The Hard Way". 
We'll work through examples, interacting
with the database over the command line interface, and creating a small sample database
of pets, people, and pet shelters. 

If you're using OSX or Linux, chances are you already have SQLite installed. SQLite
stores the entire database in one file, so all we need in order to use it is a program that 
can read and write this file properly. The terminal application is called "sqllite3", and
when called with a file name, will open an interactive session with a database
named for the filename. If the database file does not exist yet, the database (and thus
its file) will be created in the current working directory.

To find out if SQLite is already installed on your system, try the below ::

    $ sqlite3 test.db
    SQLite version 3.8.3.1 2014-02-11 14:52:19
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"
    sqlite> 

If this doesn't work, then you need to install the sqlite terminal application.
Head over to the sqlite website and download the binaries for your system:

If you've worked with a regular database system before, you may be wondering 
when and where you install the database server. SQLlite doesn't use a server application,
the whole works are contained in one file and all we do is install either a terminal application
to talk to it directly or import the sqlite3 library to connect to it with Python.
SQLlite can even use an in-memory database that will cease to exist when you exit
your application. If you start SQLite without a file name, it will open a session with
a temporary in-memory database.

TODO: proper install instructions.

When we work with any RDBMS, there are two dialects that we can use to talk
to the database: vendor neutral SQL, and the vendor specific commands for the
database system. We'll be using
SQL to create, delete, or edit tables and to select or update rows within those tables.
We'll use the SQLlite commands to list all the tables in the database and to see
the details of a table's structure.

SQL commands are case insensitive and always end with a semi-colon; a command can span multiple lines and 
does not get terminated until a semi-colon is entered. SQLite specific commands 
begin with a period and are ended with a carriage-return. Confusing these two is 
a common source of confusion for new users.

For example, to list all the tables in the current database after we have 
started sqlite, we issue the SQLite **.tables** command:

    sqlite> .tables
    Person Pet
    
To see the details for a specific table, such as the Pet Table, we use the
**.schema** command 
    
    sqlite> .schema pet
    CREATE TABLE pet (
        id int primary_key not null,
        name text not null,
        age  int 
    );
 

We can always see all available SQLite commands with the help command:

    sqlite> .help

And to exit the session, we press Control-D.


To load a database from an SQL file, we'll use the redirection operator and 
a filename. 
Given a file of SQL commands, this will execute all the commands in the file.
This is called an SQL dump and is commonly used as a cross-platform way of storing or restoring the contents of
a complete database. The command below will
run the contents of the file 'pet_and_species_tables.sql' in the database
named 'pets.db', creating the database if it does not exit yet.

    $ sqlite3 pets.db < pet_and_species_tables.sql 

However, if we run the above command and don't have any errors, we don't see
any result messages in our terminal. To see what is happening as the
commands are executed, we can add the echo flag:

    $ sqlite3 -echo pets.db < pet_and_species_tables.sql 
    drop table if exists Pet;
    drop table if exists Person;
    
    create table Pet (
        id int primary_key not null,
        name text not null,
        age  int 
    );
    
    create table Person (
        id int primary_key not null,
        first_name text not null,
        last_name text not null,
        age  int 
    );

    insert into pet values 
        (1, 'Titchy', 17),
        (2, 'Snufkin', 12),
        (3, 'Tiger', 4),
        (4, 'Kismet', 9);


Now that our database has a couple of tables, we can
connect to it at the terminal and verify the contents. Note
again that we do not end our sqlite commands with a semi-colon:

    $ sqlite3 pets.db
    SQLite version 3.8.3.1 2014-02-11 14:52:19
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"
    sqlite> .tables
    Person  Pet   
    sqlite> .schema Person
    CREATE TABLE Person (
        id int primary_key not null,
        first_name text not null,
        last_name text not null,
        age  int 
    );
    sqlite> .schema Pet
    CREATE TABLE Pet (
        id int primary_key not null,
        name text not null,
        age  int 
    );
    sqlite>


To save a complete database in SQL, we will use the redirection operator
in combination with the .dump command. Note that this command is exectued
from the terminal *before* connecting to SQLite. After dumping the database
we use the 'cat' command to look in the contents of the resulting SQL file:

    $ sqlite3 pets.db .dump > pet_dump.sql
    $ cat pet_dump.sql
    PRAGMA foreign_keys=OFF;
    BEGIN TRANSACTION;
    CREATE TABLE pet (
        id int primary_key not null,
        name text not null,
        age  int 
    );
    INSERT INTO "pet" VALUES(1,'Titchy',17);
    INSERT INTO "pet" VALUES(2,'Snufkin',12);
    INSERT INTO "pet" VALUES(3,'Tiger',4);
    INSERT INTO "pet" VALUES(4,'Kismet',9);
    CREATE TABLE person (
        id int primary_key not null,
        first_name text not null,
        last_name text not null,
        age  int 
    );
    COMMIT;


The last thing we'll do before moving on to "SQL The Hard Way" is execute
an SQL command at the SQLite terminal, selecting everthing in the Pet table. 

    sqlite> select * from Pet;
    1|Titchy|17
    2|Snufkin|12
    3|Tiger|4
    4|Kismet|9
    sqlite>  


Now that have successfully connected to SQLite and created a database, we're going
to start "SQL The Hard Way". You'll be creating new tables as you follow along
with "SQL The Hard Way", so you can either delete the tables you've created 
so far or create a brand new database by erasing your database file and starting
over. Below are the SQL commands to drop our two tables:

    sqlite> drop table pet;
    sqlite> drop table person;
    sqlite> .tables
    sqlite>

     
