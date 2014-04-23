
Great resource for SQL:
Learn SQL The Hard Way: http://sql.learncodethehardway.org/book/
- uses sqlite, talk to Ben about whether we'll use sqlite
- check whether postgress has the replace/insert or replace command for ex 11
- check on PG compatibility for ex 12
- ex 13 has an assignment, do we want them to do that one or not??
- up to ex 13 is basic CRUD, definitely have them do that
- ex 14 introduces transactions
- ex 15 is an esssay on database modelling
- that's as far as Zed has got, and it's in alpha, but it's really good
- it should probably take a few hours to go through the tutorials up to ex 15.

- might be better to have them only go up to ex 12 and then explain transactions 
  ourselves separately. it's not going to be helpful to have them do 
  the assignment in ex 13 which changes the db a *lot*.


- it uses a pet database, with Pets and people. I can make sure my sample
  db is table compatible with his 

- things it does not cover:
  - examples of association objects
  - querying with the other join syntax, we should show both
  - explanation of the cartesian product for joins

Zed's pet database:

Person:
  id
  first_name
  last_name
  age

Pet
  name
  breed
  age
  dead    
