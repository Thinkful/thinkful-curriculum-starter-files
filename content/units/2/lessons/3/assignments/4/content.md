In the previous assignment you saw how to write unit tests in Python using the `unittest` module.  Now let's try to put this into practice. We are going to continue to work on the invoice divider from assignment 1, adding tests to make sure that our code is working correctly.  You can either work from your existing code, or use the code in [this gist](https://gist.github.com/oampo/547573ecd8d48a56ffd4) as a starting point.

# Creating the test class

To get started `cd` into the folder which contains your code and create a new file called `test_invoice_calculator.py`.  In that file we can add a stub for our test class:

```python
import unittest

class InvoiceCalculatorTests(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
```

Here we import the `unittest` module, and create a new subclass of `unittest.TestCase` called `InvoiceCalculatorTests`.  In our main block we call the `unittest.main` function, which will collect and run any tests which are contained in the file.

Save the file, then try to run it using `python test_invoice_calculator.py`.  You should see the following output:

```

----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK
```

This tells us that we didn't run any tests (which is unsurprising, as we haven't written any yet), and that there were no test failures.

# A simple first test

So let's start off by writing a test for our example, with Alice and Bob working for 3 hours, and Carol working for 6 hours on a $360 project.  We are going to call the `divide_pay` function with our input, and make sure that the pay is calculated correctly.

```python
import unittest

from invoice_calculator import divide_pay

class InvoiceCalculatorTests(unittest.TestCase):
    def testDividedFairly(self):
        pay = divide_pay(360.0, {"Alice": 3.0, "Bob": 3.0, "Carol": 6.0})

        # Check that the right values are returned
        self.assertEqual(pay, {"Alice": 90.0, "Bob": 90.0, "Carol": 180.0})

if __name__ == "__main__":
    unittest.main()
```

The first change we have made is to import the `divide_pay` function from our *invoice_calculator.py* file.  Next we have created a new test, called `testDividedFairly`.  In this method we call the `divide_pay` function for our scenario.  Then we use the `assertEqual` method of the `TestCase` class to check that the value returned matches our expectations for what each person should be paid.

Try running the test using `python test_invoice_calculator.py`.  You should see that we are now running one test which is passing correctly.

# Testing the edge cases

At this point our test passes, so we know that our code works right?  Well, not quite.  Generally once we have tests for the basic operation of some code we then want to identify any *edge cases* to make sure that they work properly too.  Edge cases are places where there is something slightly unusual about the input which could affect the output.  These are amongst the most common places to find bugs in code, and so are great things to test.

So let's try to look at adding tests for some edge cases to see whether we can make our code more robust.  First of all let's add a test to make sure that if we enter zero hours for a person then it is handled correctly:

```python
    def testZeroHourPerson(self):
        pay = divide_pay(360.0, {"Alice": 3.0, "Bob": 6.0, "Carol": 0.0})
        self.assertEqual(pay, {"Alice": 120.0, "Bob": 240.0, "Carol": 0.0})
```

Try running the test.  You should see that our code handles this case well already.  Now how about if none of the staff have entered any hours?  Presumably at this point we should throw an appropriate error to say that there is an incorrect input.  So let's try to write a test for that:

```python
    def testZeroHoursTotal(self):
        with self.assertRaises(ValueError):
            pay = divide_pay(360.0, {"Alice": 0.0, "Bob": 0.0, "Carol": 0.0})
```

Here we use a construct our assertion in a slightly different way.  Because we are expecting an error in the code we have to catch the exception.  In order to do this we can use a `with` block to assert that a `ValueError` is raised when we don't enter any hours.

Try running the tests.  Our new test should fail, telling us that a `ZeroDivisionError` took place when we try to work out the `per_hour` amount.  So let's make a slight change to *invoice_calculator.py* to make sure that the more appropriate `ValueError` is thrown when we have no hours entered:

```python
def divide_pay(amount, staff_hours):
    """
    Divide an invoice evenly amongst staff depending on how many hours they
    worked on a project
    """
    total_hours = 0
    for person in staff_hours:
        total_hours += staff_hours[person]

    if total_hours == 0:
        raise ValueError("No hours entered")

    per_hour = amount / total_hours

    staff_pay = {}
    for person in staff_hours:
        pay = staff_hours[person] * per_hour
        staff_pay[person] = pay

    return staff_pay
```

Notice how we've added the check to make sure that the `total_hours` variable isn't equal to zero.  Now try running the tests again.  They should now all be passing.

Let's now continue with one more edge case.  What happens if we pass an empty dictionary for the `staff_hours` variable?  Hopefully this will be handled by the `ValueError` code we've just added, so let's add a test to make sure that this also works how we expect:

```
    def testNoPeople(self):
        with self.assertRaises(ValueError):
            pay = divide_pay(360.0, {})
```

Try running your tests.  Hopefully they should all still pass, with our ValueError exception catching both scenarios where no hours are entered.

# Is this everything?

In this assignment we've seen how to test the main functionality of some code, and added a series of further tests making sure that the edge cases are covered.

Have a think about whether we've covered all of the edge cases which could arise.  Can you think of any more tests which we could add to help make our code more robust?  Remember that as a developer you will have to both write and maintain your tests, so you will need to strike a balance over the number of tests you have for each unit of code.  Be sure to discuss this with your mentor, and add any further tests which you decide are appropriate.