import json
from functools import wraps

from flask import request, Response


def accept_json(func):
    """
    Decorator which returns a 406 Not Acceptable if the client won't accept JSON
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "application/json" in request.accept_mimetypes:
            return func(*args, **kwargs)
        data = json.dumps({"message": "Request must accept JSON"})
        return Response(data, 406, mimetype="application/json")
    return wrapper

def require_json(func):
    """
    Decorator which returns a 415 Unsupported Media Type if the client sends
    something other than JSON
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if (request.mimetype ==  "application/json"):
            return func(*args, **kwargs)
        data = json.dumps({"message": "Request must contain JSON"})
        return Response(data, 415, mimetype="application/json")
    return wrapper
