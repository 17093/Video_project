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
#database file link
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
        #hash_password = generate_password_hash(password, method='SHA256')
        cursor = get_db().cursor()
        #gets cursor and compares the credentials
        find_user = ("SELECT * FROM users WHERE username = ?")
        cursor.execute(find_user,(username,))
        results = cursor.fetchone()
        if results:
            #compares the given password and the hashed password in the database
            hash_compare = check_password_hash(results[2],password)
            ###THERE IS NO ERROR MESSAGE WHEN NO PASSWORD###
            if hash_compare == True:
                session["user"] = username
                session["user_id"] = results[0]
                Logged = True
                return redirect(url_for("dashboard"))
            else:
                error= "Invalid Credentials, Please try again"
        #if user is already logged in, it will redirect to dashboard.
        #if not, it will reload login.html.
        else:
            error = "Invalid Credentials, Please try again"
    return render_template("login.html", error = error)


#dead route, 
@app.route('/signup', methods = ['GET', 'POST'])
def signup():

    return render_template(url_for('signup'))


#main index page of the website, user is directed to this page when they open this website
@app.route('/', methods = ['GET', 'POST'])
def dashboard():
    count = 0
    username = ""
    error = ""
    #if user is in the session/logged in, it lets the user pass and access the dashboard
    if "user" in session:
        title_text = ""
        username = session["user"]
        session["logged"] = True
        #cursor will obtain the urls, video names, descriptions, tags, username to display on webpage
    if request.method == "POST":
        sql = ("SELECT url.id, url.url, url.desc_name, url.desc, users.username, tags.tag_type FROM url JOIN users ON url.uploader=users.id JOIN tags ON url.filter=tags.id WHERE filter = ?")
        values = []
        #creates a for loop for amount of tags that needs to be searched for, adding a "Or filter = ?" creating a query. 
        #it will also add more values to the count variable to keep count of how many "Or filter = ?" were added
        for k,v in request.form.items():
            if count > 0:
                sql += " OR filter = ?"
            values.append(v) 
            count +=1
        #adds the order query at the end of the sql query.
        sql += " ORDER by url.id DESC "
        print (sql)
        print (count)
        #if count is higher then 0, meaning that there are a filter query, the webpage will use the previously made query to
        #fetch the needed information from the databse and display on the webpage
    if count > 0:
        cursor = get_db().cursor()
        cursor.execute(sql,values)
        results = cursor.fetchall()
        #if there are results, it will display the filtered results on the webpage
        print (results)
        if results:
            print ("the!")
        #if there are no results, it will display an error message and redirect to main page
        else:
            print ("not here!")
            error = "Looks like there are no videos with this tag exists yet!"
            title_text = ""

    #if the count was not higher than 0, meaning that there were no filter query, will just fetch the normal view of the webpage, all the videos will be shown  
    else:
        cursor = get_db().cursor()
        cursor.execute("SELECT  url.id, url.url, url.desc_name, url.desc, users.username, tags.tag_type FROM url JOIN users ON url.uploader=users.id JOIN tags ON url.filter=tags.id ORDER BY url.id DESC ")
        results = cursor.fetchall()
        title_text = "Recent Uploads"
    print (results)
    #fetches all tag types
    cursor2 = get_db().cursor()
    cursor2.execute(" SELECT * FROM tags ")
    #applies to the tag/filter bar on left
    tag_results = cursor2.fetchall()

    title_text = "Recent Uploads"
    return render_template('dashboard.html', user = username, urls = results, page_name = "Home", tags = tag_results, error = error, title_text = title_text)

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

        #gets tags from the sql database
        cursor = get_db().cursor()
        filter_tag = ("SELECT id, tag_type FROM tags")
        cursor.execute(filter_tag)
        filter_tags = cursor.fetchall()


        #when a url of a youtube video is posted, the parse function will obtain the code.
        if request.method == "POST":
            #gets all the needed imformation from the user's input

            uploader = session.get("user_id")
            url = request.form.get("youtube")
            desc_name = request.form.get("title")
            desc = request.form.get("description")
            tag = request.form.get("tag")
            
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
                    insert_url = ("INSERT INTO url (url, desc_name, desc, uploader, filter) VALUES (?, ?, ?, ?, ?);" )
                    cursor.execute(insert_url,(v, desc_name, desc, uploader, tag))
                    get_db().commit()
                    #refreshes the page to empty the input boxes
                    return redirect(url_for('upload'))
                     
                #error message     
                else:
                    error = "error, please check the url again"
        return render_template('upload.html', error = error, page_name = "Upload", tags = filter_tags)
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
        #redirects user to dashboard
    return redirect(url_for("dashboard"))

#@app.route('/video/<url>')
#def show_video(url)
    #shows more informations about the video

#renderes the about page for the webpage
@app.route('/about')
def about():
    return render_template("about.html", page_name = "About")


if __name__ == '__main__' :
    app.run(debug=True)
