In the first lesson in this course, when you did the exercises on datetime objects, you briefly encountered an example of string formatting that looked like this:

```python
from datetime import datetime
now = datetime.now()
print '%s-%s-%s' % (now.year, now.month, now.day)
```

The print statement there would output something like `2014-5-13`. In this example, the three '%s' instances get substituted by string representations of the three items in the tuple that follows. 

This is just one of example of string formatting, and Python offers a number of powerful methods that allow you to substitute in variable values into strings and format data into a particular string format. 

String formatting is something you'll use again and again in your programs to do things like log information about what the program is doing and generate text based on data models. 

In this assignment, we'd like you to learn more about string formatting so you'll recognize it when you see it, and be able to use it when you need it.  Carefully read through this [tutorial on the .format() method](http://ebeab.com/2012/10/10/python-string-format/), and make sure you understand the two different approaches to string formatting using `%` vs. `.format()`.