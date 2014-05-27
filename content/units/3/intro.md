<!-- 
name: Working with Databases Intro
author: Iain Duncan
type: intro
time: TBD
 -->

In this unit, we'll explore data persistence using [SQL](http://en.wikipedia.org/wiki/SQL) (structured query language) and relational databases and  relational databases management systems (RDBMS). A relational database is one in which data is represented in tables of columns and rows. If you've ever worked with spreadsheets, you already have a good mental model of what a relational database is. SQL is a language used for working with data held in RDBMS. RDBMS provide a way to flexibly and consistently represent structured data, and they make it possible for many users to simultaneously access a data store while maintaining data integrity. 

Database *transactions* make it possible for us to group a set of operations together and ask the system to allow either all of them to succeed or prevent any from succeeding. The classic example of this is a banking system: many different users may be accessing the same account information at once, but 
when transfering funds from one account to another, either the withdrawal *and*
the deposit should succeed, or neither.

As we said, SQL is the common language used to interact with relational databases. SQL is a [declarative language](http://en.wikipedia.org/wiki/Declarative_programming) used to interact with modern relational database management systems. Although there are numerous popular database systems like MySQL, PostreSQL, and Oracle, SQL is the language you use to interact with all of them. And while there are a number of new non-SQL based persistence 
tools available like MongoDB, CouchDB and Redis, SQL databases continue to be
by far the most common way of persisting data for web applications. 

Usually when we hear the term "database layer" in an application context, this refers to an SQL database that our Python application code interacts with. When we run a Python web application on a server, there may be many users concurrently accessing the server, each using a different thread of the Python application. By connecting to a transactional database that can handle concurrent access, we are able to have our application deal with real world issues without concurrency conflicts. There are numerous contexts where managing concurrency conflicts is critical: ticket selling applications,
shopping carts that sell items of limited stock, reservation systems, etc.
While SQL is itself not part of the Python language, it's important that a Python developer be comfortable using SQL to properly design and implement a storage backend.

In this Unit we will use two different SQL database systems: SQLite and PostgreSQL. SQLite is an open-source minimal database system that stores all data in a single local file. SQLite is primarily used for learning SQL, prototyping apps, and embedding databases in small applications (for instance, SQLite is the database used in many mobile devices). As a result, it's the most widely deployed database system in the world. 

PostgreSQL, on the other hand, is an open-source, industrial strength, full featured database server. Along with MySQL, it's one of the most commonly used database layers for dynamic web applications.

This Unit consists of three lessons. First we'll install SQLite and work with it to learn the SQL language. In the second lesson, we'll learn how to use Python as a scripting language to interact with SQLite and with PostgreSQL databases. Finally, in the third lesson, we'll learn about a powerful database toolkit for Python called SQLAlchemy, and learn how to use its Object Relation Mapper (ORM). ORMs streamline the writing of database applications in Python and are often used as the glue layer between Python programming with objects and the SQL database layer. SQLAlchemy is the ORM we'll use in Unit 4 when we begin building web applications with Flask.

# Goals

*   Learn SQL basics 
*   Learn how to use Python to interact with SQLite and PostgreSQL databases
*   Learn about ORMs and how to use SQLAlchemy 






