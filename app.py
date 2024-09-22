#Imports

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import requests
import pyrebase
import json
from json import tool

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

#API URL

API_KEY = "p9ItqZXnSAiTr9gbLQ8Bu0ObrwKwaRHTtxU5XBsY"

database_URL = "https://images-api.nasa.gov/"
apod_URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

#Code goes below here

firebaseConfig = {
    "apiKey": "AIzaSyCa5S6ESqMiS7aUn3kMvkz6OIRESHyN0HU",
    "authDomain": "y2-2024-summer.firebaseapp.com",
    "databaseURL": "https://y2-2024-summer-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "y2-2024-summer",
    "storageBucket": "y2-2024-summer.appspot.com",
    "messagingSenderId": "1003158324492",
    "appId": "1:1003158324492:web:423017e3297ebb9aac7529",
    "measurementId": "G-B3Y6Q8GHF7"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()


#Routes go below here

@app.route("/")
def index():
    login_session['user'] = None
    auth.current_user = None
    return render_template("index.html")

#Sign up, in and out

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        description = request.form['description']

        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            user_data = {
                'username': username,
                'email': email,
                'password': password,
                'description': description,
            }
            db.child("Users").child(login_session['user']['localId']).set(user_data)
            return redirect(url_for('home'))
        except:
            error = "Failed, try again"
            return render_template('signup.html', error=error)
    return render_template('signup.html', error=error)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except:
            error = "Failed, try again"
            return render_template('signin.html', error=error)
    return render_template('signin.html', error=error)


@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))

#Home route

@app.route('/home', methods=['GET', 'POST'])
def home():
    if auth.current_user is None:
        redirect(url_for('signin'))
    return render_template('home.html')

#APIs

@app.route('/nasaImages', methods=["GET", "POST"])
def nasaImages():
    if auth.current_user is None:
        redirect(url_for('signin'))

    error = ""
    image_url = "../static/assets/img/Mars/mars-surface.jpg"
    title = "Example: Mars surface from a rover"
    if request.method == "POST":
        search = request.form["search"]
        params = {
            "q": search,
            "media_type": "image"
        }
        try:
            req = requests.get(database_URL + "/search?", params=params)
            data = req.json()
            items = data["collection"]["items"]
            title = items[0]["data"][0]["title"]
            image_url = items[0]["links"][0]["href"]
            return render_template('nasaImages.html', image_url=image_url, title=title)
        except:
            error = "Something went wrong, search for something else"
            return render_template('nasaImages.html', image_url=image_url, title=title, error=error)
    return render_template('nasaImages.html', image_url=image_url, title=title, error=error)


@app.route('/APOD', methods=["GET", "POST"])
def apod():
    if auth.current_user is None:
        redirect(url_for('signin'))

    params = {
        "api_key": apod_URL,
        "hd": True,
        "count": 1
    }
    req = requests.get(apod_URL, params=params)
    data = req.json()
    title = data[0]["title"]
    img_url = data[0]["url"]

    return render_template('pod.html', title=title, img_url=img_url)

#Profile management

@app.route('/update', methods=["GET", "POST"])
def update():
    error = ""
    if request.method == "POST":
        description = request.form['description']
        username = request.form['username']
        try:
            user_data = db.child("Users").child(login_session['user']['localId']).get().val()
            db.child("Users").child(login_session['user']['localId']).set({"email": user_data.get("email"), "password": user_data.get("password"),"username": username, "description": description})
            return redirect(url_for('profile'))
        except:
            error = "Failed, try again"
            return render_template('update.html', error=error)
    return render_template('update.html', error=error)


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if auth.current_user is None:
        redirect(url_for('signin'))

    user_data = db.child("Users").child(login_session['user']['localId']).get().val()

    return render_template('profile.html', user_data=user_data)


if __name__ == '__main__':
    app.run(debug=True)

# params = {
#     "q": "apollo 11",
#     "media_type": "image"
# }
# print(API_URL)
# req = requests.get(API_URL + "/search?", params=params)
# data = req.json()
# items = data["collection"]["items"]
# image_url = items[0]["links"][0]["href"]
# print(image_url)
