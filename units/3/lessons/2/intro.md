[//]: <> (name: PostgreSQL, Python and Psycopg2)
[//]: <> (author: Benjamin White)
[//]: <> (type: intro)

#  PostgreSQL, Python and Psycopg2

Now that we've learned the basics of SQL using SQLite, in this lesson we'll learn how to work with [PostgreSQL](http://www.postgresql.org/), which is a robust, production ready, open source database. As we noted in the introduction to this Unit, PostgreSQL is one of several production ready databases available. You've probably heard of MySQL which has been around longer and is widely used, and you may have heard of Oracle, which is a proprietary relational database. We've chosen to teach PostgreSQL in this course because it is the RDBMS used by Heroku, which we'll use in Units 4 and 5 to deploy our web apps. 

In this lesson, we'll first get PostgreSQL installed and configured in our local development environment. After that, we'll discuss the key differences between working with SQLite and PostgreSQL. After that, we'll learn how to use [psycopg2](http://initd.org/psycopg/), which is a Python wrapper around PostgreSQL that allows you to work with the database using the Python programming language.


### Goals

*   Install and configure PostgreSQL 
*   Learn how to use psycopg2 to create databases and query and modify tables
