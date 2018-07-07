# server.py
import os, random, requests
import base64, hashlib
from functools import wraps
from flask import Flask, render_template, request, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="../static/dist", template_folder="../static")
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
version = '1.0.4'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<Name %r>' % self.name

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(60))
    title = db.Column(db.String(200))
    description = db.Column(db.String(500))
    starting_price = db.Column(db.Numeric(2))
    time_created = db.Column(db.DateTime())

    def __init__(self, user, title, description, starting_price, time_created):
        self.user = user
        self.title = title
        self.description = description
        self.starting_price = starting_price
        self.time_created = time_created

    def __repr__(self):
        return '<Listing %s>' % (self.id)

class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True)

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return '<Key %s>' % (self.id)

def addToDB(obj):
    db.session.add(obj)
    db.session.commit()

def deleteFromDB(obj):
    db.session.delete(obj)
    db.session.commit()

def generate_hash_key():
    return base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(),
                            random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')

def create_and_store_key():
    key = Keys(generate_hash_key())
    addToDB(key)
    print(key.key)

# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.form['key'] and request.form['key'] == Keys.query.filter_by(id=1).first().key:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

@app.route("/create/user", methods=['POST'])
@require_appkey
def create_user():
    try:
        name = request.form['name']
        password = request.form['password']
        userExists = User.query.filter_by(name=name).first()
        if userExists:
            return "Username taken"
        else:
            user = User(name=name, password=password)
            addToDB(user)
            return "success"
    except:
        return "Unexpected error"

    return 'Success'

@app.route("/delete/user", methods=['DELETE'])
@require_appkey
def delete_user():
    try:
        name = request.form['name']
        user = User.query.filter_by(name=name).first()
        deleteFromDB(user)
    except:
        return "Unexpected error"

    return 'Success'

@app.route("/get/user/<name>", methods=['GET'])
def get_user(name):
    try:
        user = User.query.filter_by(name=name).first()
        if not user:
            return 'User:%r not found' % (name)
        return str(user.name)
    except:
        return 'Unexpected error'

@app.route("/validate_login", methods=['POST'])
@require_appkey
def validate_login():
    try:
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()
        if not user:
            return 'User: %r not found' % (name)
        elif user.password == password:
            return 'success'
        return 'Incorrect Password'
    except:
        return 'Unexpected error'

@app.route("/create/listing", methods=['POST'])
@require_appkey
def create_listing():
    try:
        title = request.form['title']
        user = request.form['user']
        description = request.form['description']
        starting_price = request.form['startingPrice']
        time_created = request.form['timeCreated']
        listing = Listing(user=user, title=title, description=description, starting_price=starting_price, time_created=time_created, )
        addToDB(listing)
    except:
        return 'Unexpected error'

    return 'Success'

@app.route("/health")
def test():
    return 'Server is up and functional. Version ' + version

if __name__ == "__main__":
    app.run(port=8080)