Unit 3 Introduction
===================

In this unit we'll be covering persisting your program data using SQL and
relational databases. Relational Databases Management Systems (RDBMS) 
are an excellent way to persist 
data: they can represent structured data flexibly and consistently, and they
allow many users to simultaneously access a data store
while maintaining data integrity. Database *transactions* make it possible for us 
to group a set of operations together and ask the system
to allow either all of them to succeed or prevent any from succeeding. 
The classic example of this is a banking system: many different users
may be accessing the same account information at once, but 
when transfering funds from one account to another, either the withdrawal *and*
the deposit should succeed, or neither.

SQL is the declarative language used to interact with
modern relational database management systems, and is a standard that we
know will work across all the major database systems, such as MySQL, PostGres, 
Oracle, and others. While there are a number of new non-SQL based persistence 
tools available, such as Mongo, CouchDB or Redis, SQL databases are still
by far the most common way to persist data in a web application. Usually when 
we hear the term "database layer" in an application context, this will be referring
to an SQL database with which our application code, Python running on a server, 
is interacting. When we run a Python web application on a server,
there may be many users accessing the server concurrently,
each using a different thread of the Python application. By connecting to a 
transactional database that can handle concurrent access, we are able to 
have our application deal with real world issues without concurrency conflicts.
You can imagine many context where this is critical: ticket selling applications,
shopping carts that sell items of limitted stock, reservation systems, etc.
While SQL is itself not part of the Python language, it's important that a Python
developer be comfortable using SQL to properly design and implement a storage backend.

In this Unit we will use two different SQL database systems, SQLite and PostGreSQL.
SQLite is an open-source minimal database system that stores all data in only one local file. It's
very popular as a database for learning, prototyping, or embedding a database
in a small application. Chances are you have SQLite running already on your phone;
as a result, it's the most widely deployed database system in the world!
PostGreSQL on the other hand is an open-source industrial strength full featured database server.
Along with MySQL, it's commonly used as the database layer in the majority
of dynamic web applications.

In the first lesson we'll install SQLite and use it to learn the SQL language and
build our sample database. The second lesson will cover using Python as a scripting 
language to interact with SQLite and with PostGreSQL. In the third lesson, we'll
cover a powerful database toolkit for Python called SQLAlchemy, and learn
how to use its Object Relation Mapper (ORM). ORMs streamline the 
writing of database applications in Python and are often used as the glue layer
between Python programming with objects and the SQL database layer.






