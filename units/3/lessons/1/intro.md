[//]: <> (name: Learning SQL with SQLite)
[//]: <> (author: Iain Duncan)
[//]: <> (type: intro)

# Learning SQL with SQLite

In this first lesson, we'll get SQLite up and running, and then we'll get a crash course in SQL as we work through part of the online book [Learn SQL The Hard Way](http://sql.learncodethehardway.org/). We'll learn how to use the command line interface to interact with SQLite databases, and create a small  sample database of pets, people, and pet shelters. We'll work with this database to learn the fundamentals of SQL: creating tables, inserting records, modifying and deleting them, and querying them.

Keep in mind that the goal here is **not** to teach you everything about SQL. You could spend an entire course focusing only on relational databases. Instead, the goal is to teach you enough about SQL that you'll have a sense of what's happening "behind the scenes" later in this course when we begin to use SQLAlchemy as an abstraction layer over our databases. 

### Goals
*   Install SQLite and learn how to work with it
*   Learn the basics of SQL