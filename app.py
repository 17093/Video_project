#Video sorting application made by Kevin Kang
from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'urlstorage.db'

#closes database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#gets database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    logged = False 
    error = None
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        print (username, password)


        cursor = get_db().cursor()
        #gets cursor and compares the credentials
        find_user = ("SELECT * FROM users WHERE username = ? AND password = ?")
        cursor.execute(find_user,[(username),(password)])
        results = cursor.fetchall()
        print("results")
        if results:
            logged = True
            return redirect(url_for("dashboard"))
        else:
            logged = False
            return redirect(url_for("dashboard"))
    return render_template('login.html')



@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__' :
    app.run(debug=True)
