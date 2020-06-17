#Video sorting application made by Kevin Kang

#hashing https://werkzeug.palletsprojects.com/en/1.0.x/utils/
#ex https://www.w3schools.com/w3css/default.asp
from flask import Flask, render_template, g, request, redirect, url_for, session
import sqlite3
from datetime import timedelta
import urllib
from werkzeug.security import generate_password_hash, check_password_hash

Logged = False
app = Flask(__name__)
app.secret_key = "bread"
app.permanent_session_lifetime = timedelta(minutes=50)
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
    
    session.pop("user", None)
    return render_template('index.html')

#login route
@app.route('/login', methods=['GET','POST'])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    session.pop("user", None)
    error = None
    Logged = False
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        cursor = get_db().cursor()
        #gets cursor and compares the credentials
        find_user = ("SELECT * FROM users WHERE username = ? AND password = ?")
        cursor.execute(find_user,[(username),(password)])
        results = cursor.fetchall()
        print(results[0][0])
        #if username and password match the database's credentials,
        #it will redirect to dashboard
        if results:
            session["user"] = username
            session["user_id"] = results[0][0]
            Logged = True
            return redirect(url_for("dashboard"))
        #if user is already logged in, it will redirect to dashboard.
        #if not, it will reload login.html.
        else:
            error = "Invalid Credentials, Please try again"
    return render_template("login.html", error = error)



@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    username = ""
    #if user is in the session/logged in, it lets the user pass and access the dashboard
    if "user" in session:
        username = session["user"]
        Logged = True
        #cursor will obtain the urls, 
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM url ORDER BY url.id DESC")
        results = cursor.fetchall()

    
        return render_template('dashboard.html', user = username, urls = results,)
    
    return redirect(url_for("login"))

#will logout users and redirect to home page.
@app.route('/logout')
def logout():
    Logged = False
    session.pop("user", None)
    return redirect(url_for("index"))
    
#will snip out the v value and obtain the code for the youtube urls.
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    username = ""
    #if user is in the session/logged in, it lets the user pass and access the upload page
    if "user" in session:
        username = session["user"]
        #when a url of a youtube video is posted, the parse function will obtain the code.
        
        if request.method == "POST":
            uploader = session.get("user_id")
            url = request.form.get("youtube")
            desc_name = request.form.get("title")
            desc = request.form.get("description")
        
            #url = "https://www.youtube.com/watch?v=gHzuHo80U2M"
            parsed = urllib.parse.urlparse(url)
            v = urllib.parse.parse_qs(parsed.query)['v'][0]
            #return str(v)
            cursor = get_db().cursor()
            #gets cursor to input the obtained youtube urls to database
            insert_url = ("INSERT INTO url (url, desc_name, desc, uploader) VALUES (?, ?, ?, ?);" )
            cursor.execute(insert_url,(v, desc_name, desc, uploader))
            get_db().commit()
            return redirect(url_for('upload'))
        return render_template('upload.html' )

        #else:
            #error = "Invalid information, please check again"
    return redirect(url_for("login"))

if __name__ == '__main__' :
    app.run(debug=True)
