import argparse
import sys

import requests

import authorization
from urls import *

def make_parser():
    """ Construct the command line parser """
    description = "Command line Twitter client"
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers(help="Available commands")

    # Subparser for the timeline command
    timeline_parser = subparsers.add_parser("timeline",
                                            help="View the timeline")
    timeline_parser.set_defaults(command="timeline")

    # Subparser for the post command
    post_parser = subparsers.add_parser("post", help="Retrieve a snippet")
    post_parser.add_argument("post", help="The tweet you want to post")
    post_parser.set_defaults(command="post")
    return parser

def get_timeline(auth):
    response = requests.get(API_URL + TIMELINE_URL, auth=auth)
    return response.json()

def post_tweet(post, auth):
    data = {"status": post}
    response = requests.post(API_URL + TWEET_URL, data=data, auth=auth)

def main():
    parser = make_parser()
    arguments = parser.parse_args(sys.argv[1:])
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    auth = authorization.get_auth()

    if command == "timeline":
        timeline = get_timeline(auth=auth)
        for item in timeline:
            print u"{} (@{})".format(item["user"]["name"],
                                     item["user"]["screen_name"])
            print item["text"]
            print ""

    if command == "post":
        post_tweet(arguments["post"], auth=auth)

if __name__ == "__main__":
    main()
