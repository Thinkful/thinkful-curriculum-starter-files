Testing Database Applications
=============================

Testing database applications requires some different approaches from 
regular unit testing. In a database application, the database is our
record of state. In addition to returning values, method calls often 
have side-effects that are written to the database. Thus we can't know
everything is working properly without verifying our postcondition state
in the database, and doing so requires us to have a specific precondition
state in the database.
This introductes a number of new concerns with regards to some fundamental
principles of writing robust tests. We'll review some of the fundamental
principles of good testing here and discuss any additional complexity that
the database adds to them. 

In this guide, we'll refer to the section of the application that is being
tested as the Software Under Test, or SUT. A "precondition" refers to any
setup or database state that is required before the SUT executes, and a 
"postcondition" is any state that is expected after the SUT executes.


Design for Testability
----------------------
When we are designing our software, we should think about how we're going
to be able to test it. Usually we want to have a method do
*one* thing. We know we've done this well if we can give the method a 
doctstring clearly stating the one thing it does. If a method returns a value,
writes to an object's state, and persists to the database, we have too much 
to verify in a test and we should consider breaking this up into multiple methods.
A good guideline is to keep reads and writes to "self" in one method, while some
other methods do logic and others handle db persistence. If it makes sense to 
calculate more than one value at a time in a method, we can either return an object 
that contains the various values or we can use Python's automatic tuple unpacking
 to return multiple values.  

Here is an example of method doing too many types of things to make 
it easy to test. We have calculations, reads and writes to self, and
persistence to the DB all in the same place.


    # a method of our shopping app
    def do_transaction(self, item_list):
        "calculate the shopping cart total, store on self, save in db"
        # these calculations are writing to the app attributes
        self.subtotal = sum( [item.price for item in item_list ] )
        if self.shopper.is_taxable():
            self.tax_total = sum( [item.price * item.tax for item in item_list] )
        else:
            self.tax_total = 0
        self.total = self.subtotal + self.tax_total
        # persist the total on the transaction
        transaction = Transaction(self.shopper, self.subtotal, self.tax_total,
            self.total)
        self.db_session.add(transaction).commit()
        # now return our transaction
        return transaction
    
A test for this is going to have to do too many different kinds of assertions,
and is going to require checking return values, application state, *and* database
postconditions.  If we break this up into several method calls, we can do it such that each 
method is easier to test.

    def do_transaction(self, item_list):
        "create a transaction record and store on self"        

        # read from self to find out if taxable
        taxable = self.shopper.is_taxable()
        
        # call method that *only* calculates
        subtotal,tax_total,total = self.calculate_totals(item_list, taxable)
    
        # call method that only handles persistence
        self.transaction = self.create_transaction(self.shopper, subtotal,
            tax_total, total)

        # Done. No return value, I'm only doing side effects 


    # new method that calculates and returns. No side effects!
    def calculate_totals(item_list, taxable):
        """
        calculate totals from item list and taxable flag
        return subtotal,tax_total, total
        """
        subtotal = sum( [item.price for item in item_list ] )
        if taxable:
            tax_total = sum( [item.price * item.tax for item in item_list] )
        else:
            tax_total = 0
        total = subtotal + tax_total
        return subtotal, tax_total, total


    # method that *only* handles persisting a transaction
    def create_transaction(self, shopper, subtotal, tax_total, total):
        "create and return a database transaction record"        

        # persist the total on the transaction
        transaction = Transaction(shopper, subtotal, tax_total, total)
        self.db_session.add(transaction).commit()
        return transaction


In our refactored version, we can see that database activity is limited
to the create_transaction method. When we test create_transaction, we'll
only be worried about verifiying that the correct values got saved and
that our transaction model is working correctly. When we test calculate_totals,
we no longer have to worry about the database at all, allowing us to move
that into a simple unit test. And our do_transaction method reads and writes values
to the self of the app.  


Tests Should Be Easy To Read
----------------------------
A thorough test suite also acts as a kind of documentation for our application.
If the test suite infrastructure is written correctly, we ought to be able to tell
at a glance what the test is doing and what it is testing. Tests should have names
and doc strings that indicate what they are expecting, variable names should indicate
at a glance what they hold, and the messages used 
for assertions should clearly state what was expected and why it failed.
Test runners have switches to print out the doc strings as tests run, so 
we can use these to keep track of what's working and what isn't: ::

    test_new_cat_defaults_alive(self):
        "test_new_cat_defaults_alive - creating a new cat should default to alive"
        cat_values = dict(name='Fifi', age=12)
        # our app got instantiated in the setup routine
        # execute the SUT
        self.app.create_cat( cat_values )
        # now check DB postconditions
        # get cat from db
        new_cat = self.confirm_session.query(Cat).filter(name='Fifi').one()
        # assertion with helpful failure message
        assert new_cat.alive == True, ( 
            "New cat.alive should be True, is: %s" % new_cat.alive)

When the above test is run in verbose mode and fails we'll see a clear message
telling us which test failed, what it was supposed to verify, and what really 
happened. When we're testing with a database, we should clearly state in the doc
string what the persistent effect should be. In our assertions, we should 
assert on variables that are pulled out from the database after the SUT has
been executed, and we should make sure our assertion strings clearly indicated
what was expected and what we got instead if the assertion fails. 

TODO: show sample for a test like the above output


Tests Should Be Fast To Write
-----------------------------
This is really the biggy. If it's hard to write a new test, it won't happen enough.
Testing is a situation where we will use as much reusable code as we can in order
to cut down how much we need to type for each test. Investing
the time to build helpful base classes and mixins (BEN: do they know what a mixin is?)
to make tests as concise as possible is always worth the time. We'll group tests 
into test classes such that pre and post test infrastracture can be repeated in generic
setup and teardown methods. We'll be looking further the next document at how this
can be achieved with a reusable test scaffold.

TODO: insert examples here?


Tests Should Not Depend on Each Other (No Fragile Tests)
--------------------------------------------------------
It should never matter what order we run tests
in, and we ought to be able to run any test in isolation. 
If a test depends on the postcondition of a previous test, it's called a 
"Fragile Test", and we can't run it in by itself. Worse, some tests could
depend on the result of a previous test and only pass if run in a specific order.
With database applications, this means we need to invest
the time in setting up a database setup and seeding routine so that 
each test gets a fresh reliable precondition database. We'll be building helper methods
to run in our test suites **setUp** and **tearDown** methods to make sure 
that any test can run anytime.


Tests Should (Usually) Test One Thing At A Time
-----------------------------------------------
This principle is more of a general rule as it's often not practical to adhere to it
too strictly. Usually we want to break our tests up so that they test one branch through our
code and test one general outcome. That said, when we get into testing applications
with multiple steps needed to get to an outcome, it's not a bad plan to have
assertions along the way as we want to fail as close to our error as possible. 
But in general, when you think something could be two smaller tests instead of
one longer one, the two smaller tests will be better. 

Ideally, our test has one (or very few) assert statements. One technique that
can help with this is to create classes for *Expecteds*. An expected is a helper
class that allows you to verify a number of conditions in one go. Often we'll have
a number of conditions that we need to verify over and over in many tests. Taking
the time to wrap this up in one helper class is very useful. We'll be looking
at Expecteds in the next assignment. 

Testing Should Require No Additional Steps
------------------------------------------
When new programmers first start to test with databases, the inclination is often
to just "keep it simple" by having an SQL file with your pre-conditition database,
filling a database from it manually, and running your test. This extra step and 
file doesn't seem too onerous at the beginning, but as tests diverge and need
very different precondition databases, this requires extra time, is error prone,
and results in too many extra files. Any extra hassle means...tests get
written less and run less. A well implemented test suite should require only 
one step: firing the test runner. It's always worth the extra time to figure out
how your test runner will take of database seeding. We'll be looking at how
we can use our suite's setUp and tearDown methods to make sure each test
is ready to run with no additional manual work.


Tests Should Run As Fast As Possible 
------------------------------------
Tests need to execute fast because if the entire collection of tests takes too long
to run, programmers won't run them all frequently enough. This seems like
a minor concern when you're starting an application as it just doesn't take long
to run the small collection of tests, but as an application (and its test suite)
grows, running tests on a real database can start to really take a while. 

Database tests that use a complete database that is torn down and rebuilt on each
test can become very slow. There are a few approaches to mitigate this.

One (slightly controversial) approach to this is to use the same starting
database for a number of tests grouped together, with a setup routine that
*puts* the database into the correct precondition state *without* having to drop
and recreate all tables. This can dramatically speed up execution for tests that use large databases.
If you are going this route, you'll know that you've done it correctly if your
setup routine means that you can still run any test in isolation and do the tests
in any order.

Database tests can also be sped up by using an in-memory databases, which can be 
created and dropped much faster. (For example, SQLite can be used in memory.)
One disadvantage to this is that one can't verify
that your test is working properly as easily by opening the database in a terminal,
but you can solve this by using a regular file backed database while writing
individual tests and switching to an in-memory database when it's time to run
the suite. You could also use pdb to stop before a test exectues if you want
to query the database directly mid test. 


Changing the Database Should Be Trivial
---------------------------------------
If the database connection string is encoded in the test file, we can't
change the database for all our tests with the flick of one switch. It should
be possible to specify what database all the tests will use in one easily
editable place. This can be accomplished
with a configuration file used by all the tests, or by storing the database connection
string in an environment variable that gets read by the test infrastructure.



