import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required,apology
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
    pwdC = request.form.get("pwdC")
    if not (username and pwd and pwdC):
        return apology("You cannot leave any of these fields empty")
    if pwd != pwdC:
        return apology("Password and its confirmation do not match")
    hashed_pwd = generate_password_hash(pwd)
    try:
        cursor.execute("INSERT INTO users (username,password_hash) VALUES (?,?)",(username,hashed_pwd))
    except sqlite3.IntegrityError:
        return apology("Username already exists")
    conn.commit()
    session["user_id"] = cursor.execute("SELECT id FROM users WHERE username = ?",(username,)).fetchone()["id"]
    return redirect("/")

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    session.clear()
    username = request.form.get("username")
    pwd = request.form.get("pwd")
    if not (username and pwd):
        return apology("You cannot leave thse fields empty")
    row = cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row is None or not check_password_hash(row["password_hash"],pwd):
        return apology("Invalid username or password")
    session["id"] = row["id"]
    return redirect("/")

    


