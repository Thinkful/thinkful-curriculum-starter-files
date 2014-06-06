We've already seen how simple it is to send data to an API using JSON.  So surely it should be equally simple to send a file in to our application?  Sadly a programmer's life is never that easy; JSON does not have a built-in way to encode binary data such as files.  This leaves us with two options, each with advantages and disadvantages:

1. We can encode the file using Base-64
    - Only one HTTP request required
    - Encoding and decoding the data takes time
    - The data we transfer will be larger
2. We can send the file as multi-part form data
    - Requires two HTTP requests - one for the file and another for the related information
    - No encoding and decoding required
    - Less data needs transferring

In this assignment we are going to choose the second option, sending the data as multi-part form data.  This is the default method used by `<form>` elements for sending data to a server.

## Test first

To get started let's put together a test which tries to upload a simple text file to the server.  In the `TestAPI` class in the *tests/api_tests.py* file try adding the following test:

```python
    def test_file_upload(self):
        data = {
            "file": (StringIO("File contents"), "test.txt")
        }

        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            contents = f.read()
        self.assertEqual(contents, "File contents")
```

There are a few things to notice here.  We construct the form data as a dictionary, using an instance of the Python `StringIO` class to simulate a file object.  We then send this dictionary to the  `/api/files` endpoint with a content type of `multipart/form-data`.  Finally we carry out a series of checks, making sure that the response data points us to a URL where we can access the file, and that the file has been saved correctly in an upload folder specified in the *chords/config.py* file.

Try running the test using `nosetests tests`.  You should see that the request fails with a `404` error.

## Writing the endpoint

Next we can write the endpoint to handle the uploads.  In the *chords/api.py* file try adding the following endpoint:

```python
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.asDictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
```

We try to access the uploaded file from Flask's `request.files` dictionary.  If we don't find the file we return an error in the usual way.

Next we use the Werkzeug `secure_filename` function to create a safe version of the filename which the client supplies.  This prevents malicious users from creating files anywhere on the server by passing in specially crafted filenames.  So for example the path *../../../etc/passwd* (which could point to the file containing the authorised users for the server) is replaced by *etc_passwd*.

We use our secure filename create the `File` object and add it to the database.  Then we can use the `upload_path` function which is defined in the *chords/utils.py* file to save the file to an upload folder.  Finally we use the `as_dictionary` method to return the file information.

Try running the test again.  We should now have a working method of uploading files to the application.

## Accessing files

Now that we can upload to our backend we need to add a route which will allow us to access the uploaded files.  So let's create a test where we add a file to our upload folder then try to access it through an HTTP request.

```python
    def test_get_uploaded_file(self):
        path =  upload_path("test.txt")
        with open(path, "w") as f:
            f.write("File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, "File contents")
```

This should all look pretty straightforward.  We create a file in the upload folder, then we send a GET request to `/uploads/<filename>`.  We check that the response contains the correct file with the right mimetype.

Now let's add our route to try to make the test pass:

```python
@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
```

Again this is very straightforward.  We use the Flask `send_from_directory` function to serve the file from the upload path.  Try running your tests again.  We should now have a way to upload and retrieve files using our API.

Try firing up the server using `python run.py` and visit the site, then upload a song using the Add Songs button.  There is an audio file called *chords.wav* in the root directory which you can use to test this out.  When the song has uploaded you should be able to select it and listen to it using the player at the bottom of the interface.

In the next assignment you will be adding an endpoint to analyse the audio data and send back the chord information.