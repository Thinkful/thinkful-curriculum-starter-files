import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from posts import app
from models import Post
from database import session
from decorators import accept_json, require_json

# JSON Schema describing the structure of a post
post_schema = {
    "properties": {
        "title" : {"type" : "string"},
        "body": {"type": "string"}
    },
    "required": ["title", "body"]
}


@app.route("/api/posts", methods=["GET", "POST"])
@accept_json
@require_json("POST")
def posts():
    """ Posts endpoint """
    if request.method == "GET":
        # Get the querystring arguments
        month = request.args.get("month")

        # Get and filter the posts from the database
        posts = session.query(Post).all()
        if month:
            posts = [post for post in posts
                     if post.datetime.month == int(month)]

        # Convert the posts to JSON and return a response
        data = json.dumps([post.asDictionary() for post in posts])
        return Response(data, 200, mimetype="application/json")

    elif request.method == "POST":
        data = request.json

        # Check that the JSON supplied is valid
        # If not we return a 422 Unprocessable Entity
        try:
            validate(data, post_schema)
        except ValidationError as error:
            data = {"message": error.message}
            return Response(json.dumps(data), 422, mimetype="application/json")

        # Add the post to the database
        post = Post(title=data["title"], body=data["body"])
        session.add(post)
        session.commit()

        # Return a 201 Created, containing the post as JSON and with the
        # Location header set to the location of the post
        data = json.dumps(post.asDictionary())
        headers = {"Location": url_for("post", id=post.id)}
        return Response(data, 201, headers=headers,
                        mimetype="application/json")


@app.route("/api/posts/<int:id>", methods=["GET"])
@accept_json
def post(id):
    """ Single post endpoint """
    # Get the post from the database
    post = session.query(Post).get(id)

    # Check whether the post exists
    # If not return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the post as JSON
    data = json.dumps(post.asDictionary())
    return Response(data, 200, mimetype="application/json")

