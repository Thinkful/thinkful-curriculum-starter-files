At the end of Exercise 4 from *LSQLTHW*, you were left with one database with three tables: one containing people, one containing pets, and one containing relationships between pets and people. This third table involves what we call a **many-to-many relationship** (often referred to as *m2m*). In our data schema we mave multiple people who can have multiple pets, and each pet can have multiple owners. Our person_pet table captures this relationship. We can say that it models an **association** between people and pets, and we can call the person_pet table an **association table** because it references both the pet and person tables. 

In the person_pet table, the 'person_id' column is what we call a **foreign key** (as is the pet_id column); it contains the integer value of the 'id' field of a row in the person table, which is the person table's **primary key**. This foreign key should only ever contain a valid primary key from the person table, as any other integer would be considered invalid. Foreign keys thus acts as connectors between the tables. In the person_pet table, we point to pets and peoples, so we can say that this table captures a symetrical, *bi-directional* relationship between two data sources. 

In contrast, **one-to-many** and **many-to-one** relationships are not bi-directional. Let's consider an example of a one-to-many/many-to-one relationship: a pet breed. A pet can only be one breed of animal (ignoring the possibility of mixed breeds for now), but we could have many pets of one breed, thus a breed could 'have' many pets. If we added a breed table to our database, inside of our pet table, we could add a new column that contains a foreign key to the breed table, replacing the text column for breed that we currently have. This would give us a many-to-one relationship between pets and breeds (note that if we put a foreign key from breeds to pets, we'd have a one-to-many relationship).

If we wanted to capture this relationship, we could create a database with the following tables:

```sql
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
```

Then, we could use the following SQL to first insert data into our breeds table, and then insert records into our pet table that reference our breed table:

```sql
insert into breed (id, name) values (1, "Tabby"), (2, "Siamese"), (3, "Persian");
insert into pet (id, name, age, dead, breed) values (1, "Titchy", 17, 1, 1);
insert into pet (id, name, age, dead, breed) values (2, "Tiger", 6, 0, 3);
```

This would give us two cats in our pets table with identical values in the column 'breed_id'. In the tables we originally created in the *LSQLTHW* exercises, we used text strings to indicate breed (for instance "Tabby"). This helps us avoid **duplication of data** in our tables, and is part of a process called **normalization** in which duplicated data is refactored out into multiple tables using foreign key relationships.

Why is **normalization** important? Let's imagine that we are running a pet shelter database, and we want to let potential adopters to search for pets by breed. Let's further imagine that the data on all the pets at the shelter is input by facility staff. What happens if one of the staff members mistakenly spells "Tabby" as "Tabbby"? If we were to query our database for records where breed = 'Tabby', we would miss this record, even though the staff member really *meant* to indicate 'Tabby', not 'Tabbby'. 

In situations like this, **data integrity** is broken. Our database doesn't *seem* to have any errors, but it's modelling an incorrect representation of reality: we have two cats of the same breed and only one will show up and get adopted, a critcal error for our application!

Another potential problem arising from duplication of data comes when updating. Let's imagine our staff member didn't know how to spell "Mayne Coon" and entered it incorrectly. In our naive implementation with a text column for breed, all the entries that used the old spelling need to be individually updated, and it's easily possible that the query to find them might miss some, and only some of our rows that should be identical get updated. This is called an **update anomaly**. In contrast, in our normalized schema, only one entry in one table needs to be changed, and we greatly reduce the chance of update anomalies.

This process of normalizing can be extended across many tables. The astute reader will notice that we have the same issue in the breed table: a breed can only be of one species but we're capturing species as a text field. This suggests we should have a single species table, and foreign key to it from our breed table.

# Follow Up Exercises:

To reinforce what you've learned in this assignment, create a new, blank database, and then write SQL code that accomplishes the following:

1.  Create a species table. This table should have a single column for "name", which should be a string value.
2.  Create a breed table. This table should have a column for "name" (text) and species (foreign key to species table).
3.  Create a pet table. This table should include the following columns: name (text), dead (integer), breed (foreign key to breed table), adopted (integer). Note that both the dead and adopted fields are intended to use 0 and 1 to refer to boolean values.
4.  Create a person table with first name, last name, age, email address, and phone number.
5.  Insert some values for species, breed, pets and people.
6.  Insert some values into the person_pet table to capture relationships.

Although you can enter the commands for each of these steps into the interactive console for the database, you utlimately should end up with a *single SQL file* that you can run from the command line that accomplishes each of these steps.  
 
When you've completed this assignment, save your file to at [Gist](https://gist.github.com/) file, and share a link with your mentor.