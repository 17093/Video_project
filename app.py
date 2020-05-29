#Video sorting application made by Kevin Kang
from flask import Flask, render_template, g, request, redirect, url_for, session
import sqlite3
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "bread"
app.permanent_session_lifetime = timedelta(seconds=10)

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

#default route
@app.route('/')
def index():
    return render_template('index.html')

#login route
@app.route('/login', methods=['GET','POST'])
def login():
    session.pop("user", None)
    error = None
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        cursor = get_db().cursor()
        #gets cursor and compares the credentials
        find_user = ("SELECT * FROM users WHERE username = ? AND password = ?")
        cursor.execute(find_user,[(username),(password)])
        results = cursor.fetchall()
        
        #if username and password match the database's credentials,
        #it will redirect to dashboard
        if results:
            session["user"] = username
            return redirect(url_for("dashboard"))
        #if user is already logged in, it will redirect to dashboard.
        #if not, it will reload login.html.
        else:
            if "user" in session:
                return redirect(url_for("dashboard"))
    return render_template("login.html")



@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        user = session["user"]
    
    return render_template('dashboard.html')
    
#will logout users and redirect to login page.
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
    

if __name__ == '__main__' :
    app.run(debug=True)
