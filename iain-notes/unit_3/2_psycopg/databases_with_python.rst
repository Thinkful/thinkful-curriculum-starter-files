Introduction to Using Database With Python
==========================================
[strarting point is pg running and filled with pets db]

Once that's done, we need to install the **psycopg** package that will Python
will use to connect to PostGreSQL. You should be able to install it with pip,
and verify that is working by importing from a Python interactive session ::

    >>> import psycopg

Ok, we're ready to move on.

Reading Documentation
---------------------     
In this lesson, we're not going to provide as much in the way of narrative 
documentation as the offical documentation for psycopg is excellent. We will
instead discuss how to read official documentation. 

Usually when learning something new, it's a good idea to work through both
a tutorial style document and the official documents. The difference is that 
the official documentation is trying to cover everything for everybody and
can be really dense. These documents often assume that we know what we're 
looking for, when sometimes we have no idea even what we are dealing with.
A tutorial on the other is unlikely to assume as much. 

On the other hand, a lot of tutorials are really out of date, or miss points.
By cross referencing between the two as we go, we'll get a pretty good idea.
Searching for "python postgres tutorial" we find two results at the top:

http://zetcode.com/db/postgresqlpythontutorial/
http://wiki.postgresql.org/wiki/Psycopg2_Tutorial

Comparing them, one is much longer than the other and seems to have a lot
of hand holding on Python basics. We decide this is a good one to come back
to if we're stuck, but we'll work through the short one (the second) first and see if it
does the job. Let's scan over it quicky just to familiarize ourselves with
the mile-high view. Read over the tutorial and come back here.

Now let's also open up the offical docs now at: http://initd.org/psycopg/docs/

What you're looking is pretty typical for a Python packages documentation.
(Well, at least for the well documented ones!) It's perfectly normal to look
at official docs and have a lot go over your head.  This is OK! The first skill
for reading documentation is to learn to find what you need amongst all the arcana.

We'll start by scanning the page quickly. We see that it's main features implement
the Python DB API 2.0 Spec, whatever that is. It might be worth opening that up. 
Looks like something that is useful to know about, but we won't spend more time on 
that until we need it.

What we probably want is the section "Basic Module Usage". We see there is also
an FAQ. That's always worth looking over even if it's mostly incomprehensible
because if there are any weird versioning conflicts, they're likely mentioned there.

Off to Basic Module Usage. Ok, this looks like the heart of it. Read up to 
"Adaptation of Python Values to SQL Types". 

We can see that the Adaptations section goes into a lot of detail for *every* type.
Again, this is a case where scanning is fine, we just need to remember that *when*
we stumble over this, this is where we should come back to. We don't need to 
read every adaptation right now. 
    
"Transaction Controls" sounds important though, so we'd better read that. (Go read!)

After that we, hit the section on Server Side Cursors. From here on down things
are pretty complicated. This is where we might scan the first couple of sentences, 
and store in our memories that if we're ever dealing with huge amounts of data,
we might want to come back to this.

At this point, we can now go *back* to our tutorial and work through it in detail,
cross referencing what we see with the offical documentation. This is really important
in case anything has changed since the tutorial was written. So now, go through the 
tutorial and make sure it's all making sense and come back.

Ok, now there's one interesting point about the tutorial, it shows us how we can
get back results in a Python dictionary and that looks really handy, but we don't 
see that anywhere in the official documentation. It turns out this very useful feature
is burried away in the Extras section of the official docs. This illustrates very
well why the official docs sometimes fail us when we don't know what we're looking for.

Now it would be a good idea to fire up your editor and make a sample script walking
through the basics we see in the tutorial: connecting, selecting, updating, disconnecting.

Exercises:
----------
Now that you've finished the tutorial, your assignment is to use Python to get your database
populated from some CSV file. A CSV file is a spreadsheet export format in which each
field is separated by a comma. In this case our first line will also have the header
information, and will look like this:

Name, age, breed name, species name, shelter name, adopted
Titchy, 12, mixed, cat, BCSPCA, 1
Ginger, 1, labradoodle, dog,,1
Snuffles, 2, labrador, dog, NYCSPCA, 0
Tiger, 8, Mixed, cat, BCSPCA, 1
Orange, , tabby, cat, BCSPCA, 0
Jake, 2,, gecko, ,1


Note that some columns are missing values, we should treat those as nulls. 
You *may* have to alter your table schema to allow these, figure that out.

1)
  - open the CSV file with Python and parse the input 
  - populate the Pet table, with only data from the columns for:
    name, age, adopted
   
2)
  - additionally populate the breed, species, and shelter tables manually
  - parse the pet csv file programmatically, inserting into the
    Pet table, with the correct foreign keys to Breed, Species, Shelter

3)
  - make a first pass through the file to populate the shelter table programmatically
    with shelter names
  - make a second pass to populate the species table
  - make a third pass to populate the breed table, with proper keys to species table
  - make a fourth pass to populate the pet table
  - note: you'll need to normalize capitalization




