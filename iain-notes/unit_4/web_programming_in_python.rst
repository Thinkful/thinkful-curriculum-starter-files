Intro to Web Programming In Python
==================================

In this unit we'll be building dynamic web applications in Python using Flask 
and SQLAlchemy. Before we get into the details of using Flask, it will help
if you have a solid understanding of how dynamic web applications in Python
work.


How Websites Work - HTTP
------------------------
To start with, let's ignore the dynamic part and take a brief side trip to
discuss how web sites work in the first place. You've no doubt heard the 
terms "client" and "server" applied to web programming. When you visit a site with
a browser, the browser is acting as the *client* program and sends a request
to the server program for a website. The server sends back text content
over the network, including HTML, and the browser knows what to do with
the HTML to make a website on the screen. One important point is that the
server can not force anything on the client, it can only *answer* requests.
This is what we call "server pull", the browser pulls in content, and the server
responds independently to each request.  

When we visit a site, our browser sends a request message, in plain text, out over the network,
and the server (such as Apache) responds with an answering message, also in plain text.
(Well it could be in encrypted text if we are using HTTPS but we'll pretend that
doesn't exist as it gets encoded and decoded for us behind the scenes!)
The protocal for these message is **HTTP**, which is not the same thing as HTML.
HTTP defines the formatting of
the text message such that the client and server understand each other in 
a standardized fashion that works for all browsers and all server applications.
When the server receives an HTTP request messages from a browser, it looks in 
the message, uses content
of the message to determine what to do, and sends back its own text message as
an **HTTP Response**. The browser then uses content from this response (such
as HTML) to draw the site on our browser's viewport. 

HTTP requests and responses have two parts: the headers and the body. They 
are simply separated from each other by a blank line in the text.
In the case of a web site page response, the body usually contains HTML.
It might also contain an image if the request is for an image file, or it
might contain some XML, some JSON, or just some information about the server.
The headers are what contain the coded information that help describe what
we want or want to get back. The important thing to understand here is that
HTTP is nothing more than a text protocal and we are just sending and receiving text messages.
We can even spy on them coming and going, and this can be very helfpul for debugging
and for understanding what's going on.


Exercise 1:
-----------
- Go install the Live HTTP Headers extension for Chrome (Note, the "HTTP Headers" extension
  is not the same as the "Live HTTP Headers" extension, the Live version shows us much more.
  You may want both, but get the Live version for this exercise. 
- Close any tabs with things like email or social networking sites open. We don't want
  anyone else making requests and cluttering up our screen!
- Click the cloud to open the headers tab, and then open another tab and visit 
  http://www.jmarshall.com/easy/http/
  (This is a pretty dense reference on HTTP, but is also a great example of the simplest 
  possible static website with a bare mininum of requests per page. You can read it
  if you *really* want to understand HTTP. )
- Notice in the headers tab that we see two requests, one for the blue ribbon image
  on the site, and the other for the HTML. Click them and look at the HTTP messages.
- Reload the page. This time we see only one request as the image has been cached on 
  our browser and doesn't need to be re-requested.
- Take a look through the request and response headers. 
  - Find the part that identifies what we want from the server.
  - Find the part that identifies our browser.
  - Find the part that identifies the size of the response we're getting back


URLS and DNS
------------
Now the role of the URL is a bit confusing. It acts both as the equivalent of a phone 
number, but also as part of the message. When we put a URL in the browser navigation tab,
the browser uses this to find the correct network address to send our HTTP message
to. It does this through a stage called DNS lookup, in which a network request is sent
out to special Domain Name Servers, prior to our main request going to the website server.
The DNS request's job is just to find the right IP address for our domain name, so you can
think of it as a request that looks in the phone book.
After we have the IP address, our HTTP request is sent on to server at that address. 
But our message also *contains* the URL 
in its headers so that the server can use this to determine what we're looking for.
As a matter of fact, there's nothing stopping us from bypassing DNS look up to
send URLs to the wrong server, and this can be very useful for testing sites 
because it allows us to emulate the exact production scenario on a different server.
(Security testers also do this to try to confuse servers!) 
We can do this be editing our "hosts" file on our computer. When our browser looks
for a site, before making a DNS request to get the IP address, it checks if we already
have this address in our hosts file. If it finds and entry in our hosts file,
it will skip DNS lookup for the domain and use the IP address from our hosts file.
We can use this to route to development servers or even our own computer. 

Exercise 2:
-----------
- Use a search engine to find out where your hosts file is on your operating system.

- Edit the hosts file to add this fake entry with a made up domain name
  192.220.73.220  www.jmarshallnewdomain.com

- Go visit our made up domain name: www.jmarshallnewdomain.com/easy/http/ 
  Note, we still get the site back properly.

- Take a look at the headers tab, and click on the new request

- You can see that we successfully sent a request to the same server, with the new 
  "hacked" domain name in the headers. However, it still worked as this server
  is only paying attention to the path, and not the host header.


Further Reading: HTTP in Detail
-------------------------------
If you would like to understand HTTP futher, not a bad idea to be sure, there is
a good tutorial at
http://code.tutsplus.com/tutorials/http-the-protocol-every-web-developer-must-know-part-1--net-31177
The Wikipedia page on HTTP is also a good resource as is the static site we visited
at http://www.jmarshall.com/easy/http/.


Static vs Dynamic Sites
-----------------------
Once our server receives the HTTP request, it can do any number of things 
depending on the contents of the URL and the rest of the request, so long as 
it always answers with a valid HTTP response message. Normally the URL contains
a domain name, used to find the right server or website on a shared server, and then a path,
used to find what we want on that specific server or site. For example, if our URL is
http://www.myserver.com/home.html, the server may be configured to look in the
directory for the mysite website and serve up the file "home.html". **Static** 
serving means that the server is just opening files, and sending back the contents
in the body of HTTP responses. A "static site" is a web site made entirely of
files served statically, so named because they aren't *dynamic*, I.E. the contents
are the same each time. A static site could have HTML files, images, CSS files, 
and Javascript files, but still have all of them served statically. Static serving
is *fast*, so even in a modern dynamic website, lots of content that doesn't 
change will be served statically, such as images and CSS files.


A dynamic site means that instead of opening a file, the server executes a program
that *builds* the file, and it then returns the output of this program as the body
of the HTTP response. If we're hitting a server, we really have no way of knowing 
if this is happening. The URL may look like /home.html and it
may seem like we're getting a file name "home.html" but that file may have been built
on the fly by a Python or Ruby or Java application. When we build dynamic websites,
what we are doing is building programs that build the text HTTP response on the fly.

When a server application such as Apache executes a program to build a site, it 
usually does it in one of three ways:

1) The server can fire up a new program to build the site, send that program a copy of
the request and return the output of the program. This is how a CGI script works,
(Common Gateway Interface) and used to be pretty much the only way dynamic websites 
were built.

2) The server can run a program *within itself* using a module, such as Apache's
mod_python or mod_php. This is common for PHP and can be done with Python using mod_python
or more commmonly now, mod_wsgi.

3) The server can **proxy** the request off to another already running program which is 
also acting as a server, and then send back the response. This means there are 
two server applications running, and the message first goes to the forward facing
server (such as Apache) which then passes it off to the next server (such as uWSGI),
which then builds the response which is returned to the first server and then to us. 
This is very common for complex modern web applications in Python.

If we wanted to, we could write a dynamic website in Python that received a 
raw HTTP request as input, manually parsed the text, and manually build a 
a text HTTP response. This would work fine, though it would be slow. This is 
essentially what CGI scripts do, and while we won't make any, it's worth looking
at one to see that, under the hood, we're just writing Python programs
that get HTTP text as input and spit back out HTTP output. 

Exercise 3:
-----------
- Go to https://wiki.python.org/moin/CgiScripts

- Take a look at the CGI script. Don't spend too long on this, just observe 
  that it's really doing nothing more than reading and printing text.

- Spot the header. There's only one.

- Find the body. Look for the code distinguishing the body from the headers.

- Be suitably de-mystified by HTTP! 


WSGI - Modern Python Sites
--------------------------
Now we've seen a complete (though simple) Python CGI dynamic site. CGI used to
be the only game in town and is still used in some places where the CGI script
is written in C and thus runs very very fast. The problem with CGI for Python
is that it takes a very long time to fire up the Python interpreter once for
every request, so while CGI is blazing fast if it's executing C that has been
compiled into machine code, it's really slow for Python. 

Nowadays Python has a the WSGI standard for applications: the Web Server Gateway Interface.
If a Python
web application is written to the WSGI spec, any WSGI enabled Python serving program
can be used to serve your website, meaning some other Python program handles
the difficult business of receiving requests, splitting off threads, keeping track of
what can be shared memory and what needs to new for each request, and so on. 
This could be an embedded module
in Apache such as mod_wsig, or a stand alone program such as uWSGI. In all cases,
our application is a Python callable with a specific *signature*. A standardized
signature means that our Python app can be anything as long as it can be called
with specifi arguments, name the WSGI environment and the start_response callable.
Our WSGI application gets imported and called by the master server application and our own
application doesn't need to worry about the intricacies of building high performance
multi-threaded servers.

The simplest possible WSGI callable app looks like the below. It's a callable
called "application", and it sends out headers for HTTP status 200 OK and Content-Type
HTML, and and HTML body:

    def application(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['<html><body>Hello World!</body></html>']

The server will import this application and use it to server our app.

We could make our WSGI application by hand, and to be honest, if you continue
in your Python programming career, learning to roll your own WSGI app
to really understand WSGI is a worthwhile exercise. But in normal situations,
we'll use a library or framework to handle turning our application
into a WSGI application that WSGI servers know how to use, so we don't need
to understand the details of WSGI engironment or start_response arguments. 

Exercises:
----------
- Take a look at this page in the uWSGI server's documentation, read up to
  "Adding Concurency and Monitoring"
  http://uwsgi-docs.readthedocs.org/en/latest/WSGIquickstart.html#the-first-wsgi-application 
- Note how we have a callable in Python file, and uWSGI takes care of importing
  it and serving it for us


Further Reading - WSGI 
-----------------------
For future reading, Python web guru Ian Bicking wrote a great tutorial on making your own
WSGI framework. When you are done with this course and want to take your 
understanding further, it's worth coming back to. It's available at
http://docs.webob.org/en/1.1/do-it-yourself.html



Frameworks and Libraries
------------------------
When we build complex applications, we face a number of concerns that are
identical or very similar to those faced by other people writing their own
applications. 
For example, any complex web site will need to have a system for finding
the right code to execute for a given incoming URL, a process called **routing**.
Unless our routing needs are very unusual, it makes sense to use
open source code created by communities of experts to handle this generic
task for us. Re-using code this way means that our own application code
is limited to that which is unique to the needs of our application, instead
of having us re-invent the wheel for common tasks. For web applications, this is not only
much more conventient for us, but also greatly improves our application security.
Web application security is very complex and seemingly innocuous errors
can expose your application to attack: using tools that have been vetted
by communities of advanced developers aware of security concerns helps
prevent us from making these mistakes. 

Some of the issues we face with a dynamic web application for which
we'll likely want to use community created code include:

* Bundling up the raw HTTP text request into a standardized Python object,
  with a nice set of convenience methods for working with it. This is 
  usually called our Request object.

* Parsing incoming URLS and routing to the appropriate code in our app,
  with some facility for writing generic routes and passing variables from
  the URL to our code.

* Simulating state so that the app "remembers" a given user between requests,
  usually by enabling some sort of **session variable** system. 

* Persisting to a database or other permanent backend persistence mechanism.

* Templating output so that we can create HTML easily and dynamically.

* Creating a proper HTTP text response from our template output,
  usually called a Response object.


All of these concerns can be handled by a number of different open source
tools, and if we wanted to, we could find **libraries** that give us tools
for each issue and glue them together ourselves. For example, the WebOb
library provides tools for creating standardized Requests and Responses in
WSGI applications, and the Beaker library can be used to create session variables.
However, this glue process 
is also something that is usually duplicated between applications, so most
web programmers will use a **framework**, in which a set of tools are 
combined in a standardized way along with helper scripts that scaffold
our application for us and get us up and running quickly. The Python
community has a large selection of both libraries and frameworks, such
as Flask, Django, Pyramid, Webob, Web2Py and more.


Inversion of Control
--------------------
The difference between a framework and a library comes down to the
principle of **Inversion of Control** (sometimes referred to as a design 
pattern itself). When we us a *library*, such as SQLAlchemy or WebOb,
we create the outer application, and our app imports the library and uses
it for a specific task. Our application *calls* the library code, and
we can decide on how our app executes itself. When we use a
framework, such as Django, the outer skeleton or architecture of the 
application is decided for us, and our app consists of creating 
components with predetermined roles. We are to some degree, "filling 
in the blanks" of a generic program. The framework calls our code, as
well as any libraries it uses.

Model-View-Controller
---------------------
Most modern web frameworks follow some variant of a design pattern
called **Model-View-Controller**. This terminology for web apps was
popularized by the Ruby-On-Rails framework for Ruby, which arguably
launched the modern *rapid application development* framework phenomena
for dynamic languages.

In an MVC app, we have separate components with separate roles, broadly 
divided into the Model, View, and Controller. These components, 
or layers as they are often called, are insulated from each other such
that the implementation details of one layer
should not be visible in any other. This principle is called **loose coupling**,
and is an important hallmark of a well designed application. Loose
coupling makes testing much easier as we can swap out components for
fake testing componentes easily to run only one subsystem in isolation.
It also means that a change or bug in one subsystem should not "leak" into
another subsytem.

The Controller layer is responsible for dealing with user input and
making decisions on how the app should respond to incoming requests.
Routing would be considered part of the controller layer as all our 
user input comes from the HTTP request. The controller might also take
input from forms or GET queries and turn them into variables for our
application. For example, given the following URL:

    www.domain.com/blog/july?_page=2

Our controller might call a Blog object, passing it a variable
for the period (july) and page number (2).

The responsibility of the Model is to handle persistence and the modelling of your 
domain logic. The model shouldn't care that it's in a web app: it's often
the database layer modelling whatever our domain problem is, such as
running a store or a bulletin board or a blog. 
With a well constructed Model, it ought to be possible to remove it from
a web application and use it by itself for testing. In our blog
example, the model might be a set of SQLAlchemy objects that persist
blog entries along with comments and archive listings to our databasebase. 

The View layer is responsible for displaying content to the user:
we say that it handles showing "views of the model". In our blog example, 
we might have an "archive view" where
the database content is used to make an HTML view of an archived posts list.
Our aforementioned Blog object could use a template system to take the
blog entires it fetches from the model and make turn them into an HTML
list.


Terminology Issues
------------------

Now there are actually some problems with this terminology that ought
to be mentioned as they can become sources of confusion to new programmers
when reading framework documentation. (Framework documentation authors love
to expound on the correct version of M-V-*!) The main issue is that the terminology
was borrowed from a design pattern for desktop applications created with
the smalltalk language. In a desktop app, MVC means something different
as all components are running on the same machine, so any component
can *call* any other component because the app is not running in a 
"server pull" environment. In "real MVC", the model can force updates
to the view, and the controller is very specifically assigned user input. 
When something changes in the back end, the view can change, *whether or not*
the user has done anything new. With a web app, this is not possible
because we are in a client-server scenario where our app can only ask 
the server for things, the server can't "push" to the browser. 

Because of this terminology confusion, subsequent frameworks have used 
variants of the term MVC
in their documentation, for example,  Django calls itself a Model-View-Template framework.
Trying to sort out the terminology at this point is a thankless task,
and will like only lead to more confusion. 
Most programmers when speaking of this family of frameworks will just call them
"MVC-style" frameworks, even though we know it's not the same as a desktop
MVC app.  The best thing for a new programmer is to just not
worry about it beyond understanding that we want our different layers and components
to have clearly defined responsibilities and not to leak into each other.
If you're interested, you can read about MVC in some detail on wikipedia,
and read the justification for why frameworks use their own terms in their
documentation, but this is absolutely not necessary for writing good apps!


Types of Framework
------------------
The division between framework and library can get a little grey with some
of the different flavours of framework.
Some are very full featured and give
you a great number of prebuilt components, but as a result force you to
"do things their way". Some are very minimal and flexible, they are almost 
like libraries that are meant
to help you build your own framework. (Some people use the term meta-framework for this).
Programmers call this difference "opinionated vs unopinionated",
some frameworks have "strong opinions" on how you should do a particular
task and others leave much more up to you. In addition some frameworks
provide more code scaffolding, some use more third party libraries than 
others, some can run in very different ways. Generally speaking, an 
opinionated framwork, such as Django, will be very productive when you are
making the type of application that is close to that for which the original 
framework was designed, and become less helpful if your application becomes
very specialized and has needs that are unique to it's own problem. For
example, it's not uncommon for a complex web apps to be prototyped in Django because
getting up and running with Django is very quick, but then later be redone
in using a more flexible unopinionated framework, such as Pyramid, 
when they get to the point that their own specialized components outnumber
the framework contribution. 

When choosing a framework, we need to weigh the pros and cons of that frameworks
position with regards to flexibility, number of components it provides,
ease of getting up and running, and so on. The dominant three frameworks in the
Python world right now are Django, Flask, and Pyramid. 

Django is a full featured monolithic opinionated framework. It provides 
a huge amount of functionality out-of-the-box, but works best when you do 
things the Django way. Because of this, one is somewhat insulated from
regular Python when writing a Django application. 

Pyramid on the other hand is minimal but extremely flexible framwork
with support for some pretty advanced programming patterns. 
It's a great framework for making large extremely loosely coupled applications
and supports component architectures very well. If your app is going
to be complex and specialized, you want to be able to choose exactly
how it works, and you know what you're doing, Pyramid is a good choice.
However, a Pyramd app forces you to be making decisions right off the start 
and is thus not a great first framework for new Python coders.

Flask sits between Django and Pyramid in many ways. Flask is also a very 
minimal and flexible, it was originally designed to be a 
a "micro-framework" allowing one to make a small site in only one Python file!
It's also a lot 
more straightforward to use than Pyramid for applications that are not
terribly complex.
Flask also uses slightly less Inversion of Control, your site
file can easily be a one file Python application that you just 
excute as normal Python program at the command line. 
We'll be using Flask in this course
as it is a good choice for small projects that don't hide exactly
what's going in Python and can be built with a minimum of files
without needing to understand the intricacies of Python package
management and web serving.

Both Flask and Pyramid are unopinionated, it's very easy to change
your persistence layer or template layer. They both use other third
party libraries for many tasks. We'll be using SQLAlchemy for our
persistence layer and the Jinja template system for HTML templating.

Exercise:
---------

- Take a look at the Wikipedia page on Flask, especially the sample app.

- You can see that our Python __main__ function servers an app, 
  created with the Flask object. One could make a case in this
  instance that Flask is being used as a library because we import 
  this class and then call it. 

- Which part of this app fulfills the Controller role?

- Is there a Model? 

