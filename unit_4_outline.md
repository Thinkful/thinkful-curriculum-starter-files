# Unit 4 Outline

## Lesson 1 - Building APIs with Flask

1. Introduction to APIs and single-pages apps (READ - Possibly http://pando.com/2012/12/06/html-javascript-and-the-app-ification-of-the-web/)

2. Writing your first endpoints (CODE ALONG)

    - mention CRUD / RESTful resource
    - Write tests for a /posts and /posts/id endpoint checking that they:
        - Return empty JSON
        - Have the correct mimetype set
    - Write minimal endpoints
        - Return empty list and dictionary at first
    - Update tests for some example data
    - Update endpoints so they return the correct data
    - Add accept header to test
    - Add accept decorator to endpoint

3. Using query strings in an API (CODE ALONG)
    - Write test checking that /posts?month=month returns the correct posts
    - Write endpoint which:
        - Retreives and returns posts from a certain month
    - **EXTENSION** Add more query types (year/month/day, author etc.)

4. Sending data to an API (CODE ALONG)
    - Write test for POST request to /posts
    - Write endpoint adding post
    - Write test for wrong mimetype
    - Add mimetype check decorator to endpoint
    - Write test for invalid data
    - Use jsonschema to validate data
    - **EXTENSION** Add PUT endpoint for editing posts

## Lesson 2 - Building a single-page app

### Project 1 - Chord tool

1. Project introduction (READ)

2. Creating a simple song management API (CODE YOURSELF)
    - Write a SQLAlchemy model for songs
    - Write test for GET to /songs and /songs/id
    - Write endpoints which:
        - Return list of/single song item as JSON
    - Write test for POST to /songs
    - Write endpoint which:
        - Validate song data supplied
        - Adds song to storage
    - **EXTENSION** Add PUT/DELETE endpoints for editing and deleting songs

3. Uploading files using an API (CODE ALONG)
    - Add location to /songs endpoints
    - Write test for POST to /files
    - Write endpoint which:
        - Takes file data as form/multipart
        - Saves file to disk in correct location

4. Writing beat and chord retrieval endpoints (CODE YOURSELF)
    - Write test for GET to /songs/id/beats
    - Pre-written function which will return list of beat times
    - Write endpoint which:
        - Returns list of beat times
    - Write test for GET to /songs/id/chords
    - Pre-written function will return list
    - Write endpoint which:
        - Returns list of chords and times as JSON
        - Returns as JSON
    - **EXTENSION** Add some extra data to the app (i.e. tempo, chord frequency)

### Project 2 - Shopping cart

1. Project introduction (READ)

2. Getting items from the database (CODE ALONG)
    - Add an SQLAlchemy model for items
    - Write tests for GET to /items and /items/id endpoints
    - Write endpoints which:
        - Query database for items
        - Return list of/single song item as JSON

3. Adding and retrieving items from the cart (CODE YOURSELF)
    - Add an SQLAlchemy model for shopping cart
    - Write tests for GET and POST to /cart
    - Write endpoints which:
        - Check whether item is in the database
        - Add the item to the cart
        - Return the list of items in the cart
    - **EXTENSION** Create way for admins to add items

4. Removing and editing items from the cart (CODE YOURSELF)
    - Write tests for PUT and DELETE to /cart and /cart/id
    - Write endpoints which:
        - Allow you to edit quantities in the cart
        - Allow you to remove items from the cart
    - **EXTENSION** Implement stock control

## Lesson 3 - Capstone


