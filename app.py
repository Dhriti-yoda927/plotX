import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from decorators import login_required
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_PERMANENT"]= True
app.permanent_session_lifetime = timedelta(days = 30)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()


@app.after_request
def after_request(response):
    #Ensures no responses are cached
    response.header["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.header["Expires"] = 0
    response.header["Pragma"] = "no-cache"
    return response

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form.get("username")
    pwd = request.form.get("pwd")
    hashed_pwd = generate_password_hash(pwd)
    try:
        cursor.execute("INSERT INTO users (username,password_hash) VALUES (?,?)",username,hashed_pwd)
    except:
        pass
    return redirect("/")


