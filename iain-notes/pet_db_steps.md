Database Design, in several passes of refactor

1) flat

  * Pet table
    * id - int, unique, PK
    * shelter id - int, unique
    * name - text
    * age - decimal
    * species - text
    * breed - text
    * adopted - boolean 
    * shelter
    

- discuss issues coming from duplicating data as text fields
Exercises:
 - selecting pets
 - inserting pets
 - counting pets with the same species
 - group by with same species


2) refactor to one-to-many keys
    
  * species table
    id, name  
  * breed table
    id, name
  * Pet table
    * fkey to species
    * fkey to breed
  * shelter
    name, address, phone, email, website
    
- discuss why this is much better:
  - we can search for a dog or terrier without worrying
   that we'll miss some because we typed in dog incorrectly to our query
  - it is much easier to correct errors later: if we find out
   that we originally spelled a breed incorrectly, we can edit one 
   record and this will be reflected in all records
- demonstrate a simple join
  - show both join syntaxes, compact and more explicit
- discuss primary keys and foreign keys

3) Update anomolies
  - we duplicate information again when we have keys from pet to both
    species and breed. A dog breed can only be a dog!
  - this leads to the possibility of an update anomoly, what if someone
    mistakenly enters Dog for species, and Ginger-Tabby for breed? our
    database is capable of happily storing an impossible situation
  - impossible situations can lead to very hard to find bugs because parts
    of the program think *nothing* is wrong, and yet you are getting invalid 
    output (ie the count of cats by species doesn't match the total count by breed!)
  - to prevent impossible situations we can validate input before putting into the 
    db (preventing with code) and/or make sure the DB can't allow bad situations
  - for a large project where *correctness* matters, it is generally better to make sure the DB can't  
    represent impossible situations
  - on the other hand, there are situations where correctness doesn't matter, 
   perhaps on a game, response time is more important than the occasional missed record
  - in our case, we are dealing with low amounts of data, and we must maintain
   correctness or a Pet might miss their chance to get adopted!
  - solution, we know that all Persians are cats, so we move the key to species
    from the Pet table to the breed table. 
  - the cost of this is that it becomes quite a bit trickier to select a pet
    by breed, we now have to daisy chain joins, demonstrate this
    

4) Problem, our db #2 assumes all pets have only one breed.
  - refactor to make a many to many table
  - pets_breeds becomes a M-to-M between pets and breeds
  - discuss how the M-to-M record makes a record of a *relationship* instead of a *thing*
  - new problem: what happens when we delete a pet? 
    - introduce cascading, we need to delete that pet's pets_breeds record  
  - now we have one-to-many and many-to-many 
  - mention UML diagrams as something to look into further with links
    - perhaps mention diagram makers such as MySQL workbench (find PG equiv!)
  
  

Hmm, not sure if the below is the right way to introduce assocs, 
perhaps look for another assoc we can add for pets
5) Problem: our current schema doesn't capture how much of each breed
  the pet is, what if we want to capture 25% rotweiller and 75% lab?
  - introduce the concept of an Association Object, this extends the idea of
   an object that describes a relationship 
  - we were not selecting records of relationships before, but now we want
   to be able to explicity ask for breed records for a pet
  - add a new field to the assoc, "amount", to capture how much of this
   breed the pet has
  - issue: we now have an abstract object that we might want to query on,
  the Pet_Breed_Assoc
  ( NB: assocs are a very good way to make shopping carts, we'll callback to this in unit 4)
  - issue: our new object doesn't *seem* to have a primary key?
  - right now, it has a logical primary key, the *combination* of pet and breed.
    - it makes now sense for us to have more than one entry for pet and breed, so we 
     can disallow that with a "constraint" : no entering the same pet/breed combo twice
   - this also *is* a primary key, it's called a *composite* primary key
  - on the other hand, we could introduce a primary key as an extra field, giving us
   one unique integer key to reference the row with,
  - however, this key is not logically necessary, that uniqueness is already captured
    by the combination. So this is called a "surrogate primary key"
  - discuss the tradeoffs:
   - for programmers, knowing that all records have a field 'id' of type int, guaranteed unique pk
     makes a lot of code reusable. We can write logic that will work with different types of objects
     the same way, as long as it knows it can count on the 'id' field.
   - for database purists, this is extra redundancy 
   - dicuss how database design is thus always balancing tradeoffs and we need to think about 
     the problem and optimal use of resource. for small projects and small teams, it is likely 
    that programmer convenienc (IE developer cost) is most important
   - but if you're Lloyds bank, absolute correctness and fault tolerance matters more.


Other possible assocs?
- pet nicknames
- pet, human relationships?
- we could then add our own pets, with the concept of nullable fkeys,
 - a pet could have no key to a shelter if he was born at home
- pets_humans would work as one pet has many humans
  - what would be the extra field for the assoc though? length of relationship?
  - tiger has been with Louise for 10 years but with me for 2 years
- this could be used to find the pets "primary care giver", it's human with the longest
  relationship
- yes, I think this is a better assoc



