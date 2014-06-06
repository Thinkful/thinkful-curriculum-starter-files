So far you have seen how to make simple command line interfaces for applications using `raw_input()` and `sys.argv` to obtain command line arguments. When you want to build more complex interfaces (think of the myriad options you can pass to the `git` command, for example), using `sys.argv` quickly becomes clunky.

In this assignment you will learn about a nicer way to handle more complex interfaces using the `argparse` module. This will give you a robust way of building command line interfaces moving forward, and we'll use argparse later in this lesson when we build our command line code snippets app.

Read through [this tutorial](https://docs.python.org/2.7/howto/argparse.html) to find out how to specify and use command line interfaces using argparse.