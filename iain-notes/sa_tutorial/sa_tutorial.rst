SQLAlchemy Tutorial

Introduction
============
Now that you have used Python and the psycopg2 driver to communicate with your database
we will look at SQLAlchemy, a toolkit that allows us to interact with a database
in a more convenient and flexible manner and write database backed code in a more readable fashion.
SQLAlchemy is a multi-level toolkit, consisting of three layers: the core, the expression
languauge, and the Object Relation Mapper. We will principally be using the ORM,
along with elements of the expression language, but we will also be using some parts from
the core to manage connections and do the database housekeeping.

SQLAlchemy is under heavy development, so it's always best to read the current SQLAlchemy 
documentation at www.sqlalchemy.org. The docs for SQLA are excellent and very detailed,
however they aren't aimed at the new programmer and assume you already understand
why you would want to use an ORM and the basics of how one works. This tutorial
will first explain what an ORM is and why we would want to use one, and then act as
a more detailed introduction to SQLAlchemy. We encourage you to read the SQLAlchemy
Object Relation Tutorial after you have worked your way through this document.


