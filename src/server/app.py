from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


#create a flask instance
app = Flask(__name__)
#App database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
#Initialize database
db = SQLAlchemy(app)


#Create a route decorator
@app.route('/')

def index():
    return render_template("index.html")

@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)