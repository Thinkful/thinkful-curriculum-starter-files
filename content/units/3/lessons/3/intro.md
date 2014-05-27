<!-- 
name: Introducing SQLAlchemy
author: Iain Duncan
type: intro
time: TBD
 -->

Now that you have used Python and the psycopg2 driver to communicate with your database we're ready to start working with [SQLAlchemy](http://www.sqlalchemy.org/), a toolkit that allows us to interact with a database in a more convenient and flexible manner and write more readable, database-backed code.  

SQLAlchemy is a multi-level toolkit, consisting of three layers: the core, the expression language, and the Object Relation Mapper (ORM). We will principally be using the ORM, along with elements of the expression language, but we will also be using some parts from the core to manage connections and do the database housekeeping.

SQLAlchemy is under heavy development, so it's always best to read the most current SQLAlchemy [documentation](http://www.sqlalchemy.org/library.html#reference). The docs for SQLA are excellent and comprehensive, however they aren't aimed at the beginner programmers and assume that you already understand why you would want to use an ORM and the basics of how one works. 

This aim of this lesson is to get you up to speed on ORMs and SQLAlchemy so that moving forward, you'll feel comfortable consulting the official docs when you don't know how to implement something. We'll discuss the purpose and benefits of ORMs and then learn the basics of working with SQLAlchemy. 

# Goals

*   Understand what an ORM is and the advantages of using one
*   Understand how to use SQLAlchemy's ORM for data persistence in Python applications
*   Learn enough about SQLAlchemy that you're comfortable consulting the official docs, moving forward.

