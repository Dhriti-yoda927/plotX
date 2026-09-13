import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash, secure_filename
from helpers import login_required,apology
from datetime import timedelta
from dotenv import load_dotenv
import hashlib

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_PERMANENT"]= True
app.permanent_session_lifetime = timedelta(days = 30)
graph_types = {
    1: "line",
    2: "bar"
}
def bar(file, filename, user_id):
    pass

def line(file,filename,user_id):
    x_col = file.columns[0]
    y_col = file.columns[1]
    ImagePath = os.path.join("uploads",str(user_id),"graphs",filename)
    #Check if this image path already exists 
    plt.plot(file[x_col],file[y_col],color = "black")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.savefig(ImagePath)
    plt.close()

graph_functions = {
    "line" : line,
    "bar" : bar
}


@app.after_request
def after_request(response):
    #Ensures no responses are cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods = ["GET","POST"])
@login_required
def home():
    if request.method == 'GET':
        return render_template("home.html")
    
    file = request.files.get("data")
    if not file:
        return apology("No file returned")
    user_id = session["user_id"]
    #Create a hash representing the data
    file_hash = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)
    conn = sqlite3.connect("users.db")
    #Checking if file already exists within database
    existing_file = conn.execute(
    "SELECT id FROM FILES WHERE user_id = ? AND file_hash = ?",
    (user_id, file_hash)
).fetchone()

    if not existing_file:
        try:
            user_folder = os.path.join("uploads",str(user_id))
            graph_folder = os.path.join(user_folder,"graphs")
            os.makedirs(user_folder,exist_ok=True)
            os.makedirs(graph_folder,exist_ok=True)
            file_name = file.filename
            cursor = conn.execute("INSERT INTO FILES (user_id,filename,file_hash) VALUES (?,?,?)",(user_id,file_name,file_hash))
            conn.commit()
            file_id = cursor.lastrowid
            file_path = os.path.join(user_folder,str(file_id))
            file.save(file_path)
        except OSError:
            conn.execute("DELETE FROM FILES where id = ?",(file_id,))
            conn.commit()
            conn.close()
            return apology("Upload wasn't succesful")
        
    else:
        file_id = existing_file[0]
    conn.close()
    return render_template("graphMenu.html",file_id = file_id)
    

@app.route("/history",methods = ["GET","POST"])
@login_required
def history():
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    if request.method == "POST":
        fileId = request.form.get("file")
        graphs = conn.execute("""
    SELECT GRAPHS.filename
    FROM GRAPHS
    JOIN FILES ON GRAPHS.file_id = FILES.id
    WHERE GRAPHS.file_id = ?
      AND FILES.user_id = ?
""", (fileId, user_id)).fetchall()
        conn.close()
        return render_template("existingGraphs.html",graphs = graphs)

    files = conn.execute("SELECT id,filename FROM FILES WHERE user_id = ? ORDER BY id",(user_id,))
    return render_template("history.html",files= files.fetchall())

@app.route("/generateGraph",methods = ["POST"])
@login_required
def generateGraph():
    graphType = int(request.form.get("graph_type"))
    file_id = int(request.form.get("file_id"))
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    fileExists = conn.execute("SELECT id FROM FILES WHERE user_id = ? AND id = ?",(user_id,file_id)).fetchone()
    if not fileExists:
        return apology("ERROR")
    path = os.path.join("uploads",str(user_id) ,str(file_id))
    file = pd.read_csv(path)
    result = conn.execute("SELECT filename FROM GRAPHS WHERE file_id = ? AND graph_type = ?",(file_id, graphType)).fetchone()
    if not result:
        graph_type = graph_types[graphType]
        filename = str(file_id) + "_" + str(graph_type) + ".png"
        if graph_functions[graph_type](file,filename,user_id):
            conn.execute("INSERT INTO GRAPHS (file_id,graph_type,filename) VALUES (?,?,?)",(file_id,graphType,filename))
            graph =  filename.removesuffix(".png")
            conn.commit()
        else:
            conn.close()
            return apology("Failed to generate graph")
    else:
        graph = result[0].removesuffix(".png")
    conn.close()
    return render_template("generateGraph.html",graph  = graph)

@app.route("/graphs/<graph>")
@login_required
def graph(graph):
    user_id = session["user_id"]
    graphName = graph + ".png"
    conn = sqlite3.connect("users.db")
    file_id = conn.execute("SELECT file_id FROM GRAPHS WHERE filename = ?",(graphName,)).fetchone()
    if not file_id:
        return apology("ERROR")
    path = os.path.join("uploads",str(user_id),"graphs",graphName)
    conn.close()
    return send_file(path)

    
        


    


"""@app.route("/graphMenu",methods = ["POST"])
@login_required
def graphMenu():
    file = request.files.get("data")
    if not file:
        return apology("No file returned")
    user_id = session["user_id"]
    file_hash = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)
    conn = sqlite3.connect("users.db")
    #Checking if file already exists within database
    existing_file = conn.execute(
    "SELECT id FROM FILES WHERE user_id = ? AND file_hash = ?",
    (user_id, file_hash)
).fetchone()

    if not existing_file:
        try:
            user_folder = "uploads/"  + str(user_id)
            graph_folder = os.path.join(user_folder,"graphs")
            os.makedirs(user_folder,exist_ok=True)
            os.makedirs(graph_folder,exist_ok=True)
            file_name = secure_filename(file.filename)
            file.save(user_folder + "/" + file_name)

        except OSError:
            return apology("Upload wasn't succesful")
        conn.execute("INSERT INTO FILES (user_id,filename) VALUES (?,?)",(session["user_id"],file_name))
        conn.commit()
    conn.close()
    return render_template("graphMenu.html")
"""







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
    session["user_id"] = cursor.execute("SELECT user_id FROM users WHERE username = ?",(username,)).fetchone()[0]
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
    row = cursor.execute("SELECT user_id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row is None or not check_password_hash(row[1],pwd):
        return apology("Invalid username or password")
    session["user_id"] = row[0]
    conn.close()
    return redirect("/")




    


