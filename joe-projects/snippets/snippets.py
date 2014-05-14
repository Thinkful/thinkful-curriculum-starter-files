import sys
import argparse
import csv

def put(name, snippet, filename):
    """ Store a snippet with an associated name in the CSV file """
    with open(filename, "a") as f:
        writer = csv.writer(f)
        writer.writerow([name, snippet])
    return name, snippet

def get(name, filename):
    """ Retrieve the snippet with a given name from the CSV file """
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row_name, row_snippet in reader:
            if row_name == name:
                return name, row_snippet
    raise NameError("Could not find the snippet named '{}'".format(name))

def make_parser():
    """ Construct the command line parser """
    description = "Store and retrieve snippets of text"
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers(help="Available commands")

    # Subparser for the put command
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet")
    put_parser.add_argument("snippet", help="The snippet text")
    put_parser.add_argument("filename", default="snippets.txt", nargs="?",
                            help="The snippet filename")
    put_parser.set_defaults(command="put")

    # Subparser for the get command
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet")
    get_parser.add_argument("filename", default="snippets.txt", nargs="?",
                            help="The snippet filename")
    get_parser.set_defaults(command="get")
    return parser


def main():
    """ Main function """
    parser = make_parser()
    arguments = parser.parse_args(sys.argv[1:])
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print "Stored '{}' as '{}'".format(snippet, name)
    elif command =="get":
        try:
            name, snippet = get(**arguments)
        except NameError as error:
            print error.message
        else:
            print snippet

if __name__ == "__main__":
    main()
