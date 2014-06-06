# Using Query Strings in an API

In this assignment we will be extending the GET endpoint for posts to allow us to carry our simple queries.  This code will allow us to find all of the posts with a title containing a particular string.

In order to perform the query we will be using query strings.  Query strings are a part of a URL designed to contain additional information which will be passed to the server in a request.  For example, take a look at the following URL:

```
http://example.com/message?from=Alice&to=Bob
```

Here the query string is the part which says `?from=Alice&to=Bob`.  This is split into two pairs of keys and values: one saying that the message is from Alice, and one saying that the message should be sent to Bob.

## Test first

Now that we know how query strings work, let's set up a test which will try to query the `/api/posts` endpoint to find posts which have a title containing the string "ham".  Try adding the following code to the `TestAPI` class in *tests/api_tests.py*.

```python
    def testGetPostsWithTitle(self):
        """ Filtering posts by title """
        postA = models.Post(title="Post with green eggs", body="Just a test")
        postB = models.Post(title="Post with ham", body="Still a test")
        postC = models.Post(title="Post with green eggs and ham",
                            body="Another test")

        session.add_all([postA, postB, postC])
        session.commit()

        response = self.client.get("/api/posts?title_like=ham",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        posts = json.loads(response.data)
        self.assertEqual(len(posts), 2)

        post = posts[0]
        self.assertEqual(post["title"], "Post with ham")
        self.assertEqual(post["body"], "Still a test")

        post = posts[1]
        self.assertEqual(post["title"], "Post with green eggs and ham")
        self.assertEqual(post["body"], "Another test")
```

This should all be pretty familiar from the previous assignment.  First we add three posts to the database, two of which contain the word "ham".  We then make a GET request to the endpoint, this time adding in our query string `?title_like=ham`.  We then check the response status and mimetype and make sure that the correct two posts have been returned.

Try running the test using `nosetests tests`.  You should see that the endpoint returns a 200 status but is ignoring our query string and giving back all three posts.

## Making it pass

Now let's try to change our endpoint to access the `title_like` value from the query string, and alter our database query so it will filter our the posts which don't match the string:

```python
@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """ Get a list of posts """
    # Get the querystring arguments
    title_like = request.args.get("title_like")

    # Get and filter the posts from the database
    posts = session.query(models.Post)
    if title_like:
        posts = posts.filter(models.Post.title.contains(title_like)))
    posts = posts.all()

    # Convert the posts to JSON and return a response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")
```

Here we use the `request.args.get` function to retrieve the value from our query string.  If there is no `title_like` key in the string this function will return `None`.

We then construct our query in a couple of steps.  First we construct a `Query` object wihout actually hitting the database.  If the query string contained a `title_like` key then we then add a filter, using the `contains` method to find titles which contain our string.  Finally we use the `all` method to actually excecute the query on the database.

Try running your tests again to make sure that our code correctly returns the filtered posts.  With this in place we now have a more powerful retrieval API which allows us to perform simple searches on our posts.

## Extension Task

Try adding a query for body text to your API.  Ideally you should be able to combine the two query types, so for example a request to `/api/posts?title_like=ham&body_like=eggs` should only return posts which have both ham in the title and eggs in the body.