#Video sorting application made by Kevin Kang, (2020)

#hashing https://werkzeug.palletsprojects.com/en/1.0.x/utils/
#ex https://www.w3schools.com/w3css/default.asp
#https://flask.palletsprojects.com/en/1.1.x/quickstart/
from flask import Flask, render_template, g, request, redirect, url_for, session
import sqlite3
from datetime import timedelta
import urllib
from werkzeug.security import generate_password_hash, check_password_hash

Logged = False
app = Flask(__name__)
app.secret_key = "bread"
#the period the user is allowed within the website until autologout 
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
#@app.route('/')
#def index():
    #logs out the user automatically
#    session.pop("user", None)
#    return render_template('index.html')

#login route
@app.route('/login', methods=['GET','POST'])
def login():
    #if user is already in session, the website automatically redirects the user to the dashboard rather than logging in again
    if "user" in session:
        return redirect(url_for("dashboard"))
    session.pop("user", None)
    error = None
    Logged = False
    #if the request method is post, it will get the username and password
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        hash_password = generate_password_hash(password, 'SHA256')
        cursor = get_db().cursor()
        #gets cursor and compares the credentials
        find_user = ("SELECT * FROM users WHERE username = ?")
        cursor.execute(find_user,(username,))
        results = cursor.fetchone()
        print (hash_password)
        print (check_password_hash(results[2],hash_password))
        #if username and password match the database's credentials,
        #it will redirect to dashboard
        if results:
            session["user"] = username
            session["user_id"] = results[0]
            Logged = True
            return redirect(url_for("dashboard"))
        #if user is already logged in, it will redirect to dashboard.
        #if not, it will reload login.html.
        else:
            error = "Invalid Credentials, Please try again"
    return render_template("login.html", error = error)



@app.route('/signup', methods = ['GET', 'POST'])
def signup():

    return render_template(url_for('signup'))



@app.route('/')
def dashboard():
    username = ""
    #if user is in the session/logged in, it lets the user pass and access the dashboard
    if "user" in session:
        username = session["user"]
        session["logged"] = True
        #cursor will obtain the urls, 
    cursor = get_db().cursor()
    cursor.execute("SELECT  url.id, url.url, url.desc_name, url.desc, users.username FROM url JOIN users ON url.uploader = users.id ORDER BY url.id DESC")
    results = cursor.fetchall()
    #print (username)
    
    return render_template('dashboard.html', user = username, urls = results, page_name = "Home")
    
    return redirect(url_for("login"))

#will logout users and redirect to home page.
@app.route('/logout')
def logout():
    Logged = False
    session.pop("user", None)
    return redirect(url_for("dashboard"))
    
#will snip out the v value and obtain the code for the youtube urls.
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    username = ""
    error = None
    #if user is in the session/logged in, it lets the user pass and access the upload page
    if "user" in session:
        username = session["user"]

        cursor = get_db().cursor()
        filter_tag = ("SELECT * FROM tags")
        cursor.execute(filter_tag)
        filter_tags = cursor.fetchall()
        print (filter_tags)


        #when a url of a youtube video is posted, the parse function will obtain the code.
        if request.method == "POST":
            #gets all the needed imformation from the user's input

            uploader = session.get("user_id")
            url = request.form.get("youtube")
            desc_name = request.form.get("title")
            desc = request.form.get("description")
            #if length of title or desc is not appropriate, it gives an error
            if len(desc_name) > 20 or len(desc) > 100:
                error = "Title or Description too long, please shorten to under 50 characters"
            elif len(desc_name) == 0 or len(desc) == 0:
                error = "Title or Description too short, please enter something into the bar"
            else:
                #url = "https://www.youtube.com/watch?v=gHzuHo80U2M"
                parsed = urllib.parse.urlparse(url)
                v = urllib.parse.parse_qs(parsed.query).get('v', [None])[0]
                #return str(v)
                if v:
                    cursor = get_db().cursor()
                    #gets cursor to input the obtained youtube urls to database
                    insert_url = ("INSERT INTO url (url, desc_name, desc, uploader) VALUES (?, ?, ?, ?);" )
                    cursor.execute(insert_url,(v, desc_name, desc, uploader))
                    get_db().commit()
                    #refreshes the page to empty the input boxes
                    return redirect(url_for('upload'))
                     
                else:
                    error = "error, please check the url again"
        return render_template('upload.html', error = error, page_name = "Upload")
    else:
        return redirect(url_for("login"))

@app.route('/delete', methods=(["GET", "POST"]))
def delete():
    if request.method == "POST":
        #Gets the video and deletes from the database
        cursor = get_db().cursor()
        id = int(request.form["video_id"])
        delete_url = ("DELETE FROM url WHERE id=?")
        #needs comma(), after the tuple
        cursor.execute(delete_url,(id,))
        get_db().commit()
    return redirect(url_for("dashboard"))

#@app.route('/video/<url>')
#def show_video(url)
    #shows more informations about the video


@app.route('/about')
def about():
    return render_template("about.html", page_name = "About")


if __name__ == '__main__' :
    app.run(debug=True)
