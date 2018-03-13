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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name

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
        user = User(name=name, password=password)
        addToDB(user)
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

if __name__ == "__main__":
    app.run(port=8080)