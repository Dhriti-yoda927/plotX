import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash, secure_filename
from helpers import login_required,apology
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_PERMANENT"]= True
app.permanent_session_lifetime = timedelta(days = 30)



@app.after_request
def after_request(response):
    #Ensures no responses are cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods = ["GET"])
@login_required
def home():
    return render_template("home.html")

@app.route("/bar",methods = ["GET"])
@login_required
def bar():
    id = session["id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    fileName = conn.execute("SELECT filename FROM DATASETS WHERE user_id = ? ORDER BY id DESC LIMIT 1",(id,)).fetchone()
    path = "uploads/" + str(id) + "/" + fileName[0]
    


@app.route("/graphMenu",methods = ["POST"])
@login_required
def graphMenu():
    file = request.files.get("data")
    if not file:
        return apology("No file returned")
    id = session["id"]
    try:
        user_folder = "uploads/"  + str(id)
        os.makedirs(user_folder,exist_ok=True)
        file_name = secure_filename(file.filename)
        file.save(user_folder + "/" + file_name)
    except OSError:
        return apology("Upload wasn't succesful")-
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO DATASETS (user_id,filename) VALUES (?,?)",(session["id"],file_name))
    conn.commit()
    conn.close()
    return render_template("graphMenu.html")







@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
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
    session["id"] = cursor.execute("SELECT id FROM users WHERE username = ?",(username,)).fetchone()[0]
    conn.close()
    return redirect("/")

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    session.clear()
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    username = request.form.get("username")
    pwd = request.form.get("pwd")
    if not (username and pwd):
        return apology("You cannot leave thse fields empty")
    row = cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row is None or not check_password_hash(row[1],pwd):
        return apology("Invalid username or password")
    session["id"] = row[0]
    conn.close()
    return redirect("/")




    


