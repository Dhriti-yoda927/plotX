from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decor_func(*args,**kwargs):
        if session.get("user_id") is None:
            return redirect("\login")
        return f(*args,**kwargs)
    return decor_func
