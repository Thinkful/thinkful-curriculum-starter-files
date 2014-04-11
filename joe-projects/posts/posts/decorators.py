from functools import wraps

from flask import request


def accept_json(func):
    """
    Decorator which returns a 406 Not Acceptable if the client won't accept JSON
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "application/json" in request.accept_mimetypes:
            return func(*args, **kwargs)
        return {"message": "Request must accept JSON"}, 406
    return wrapper

def require_json(methods):
    """
    Decorator which returns a 415 Unsupported Media Type if the client sends
    something other than JSON
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (request.method not in methods or
                request.mimetype ==  "application/json"):
                return func(*args, **kwargs)
            return {"message": "Request must contain JSON"}, 415
        return wrapper
    return decorator
