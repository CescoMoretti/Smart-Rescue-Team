from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from pickle import GET
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy



#create a flask instance
app = Flask(__name__)
#App database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
#Initialize database
db = SQLAlchemy(app)
#Create data model
class Db_data_model(db.Model):
    id =        db.Column(db.Integer, nullable=False, primary_key=True)
    name =      db.Column(db.String,  nullable=False)
    type =      db.Column(db.String,  nullable=False)
    gps_lat =   db.Column(db.Integer, nullable=False)
    gps_long =  db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer)
    battery =   db.Column(db.Integer)


#Create a route decorator
@app.route('/')

def index():
    return render_template("index.html")

@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

@app.route('/data/add', methods=['GET', 'POST'])

def add_data():
    data = Db_data_model(name= "1", type = "team", gps_lat = 12, gps_long = 145,)
    db.session.add(data)
    db.session.commit()
    istances = Db_data_model.query.order_by(Db_data_model.id)
    print(istances)
    return render_template("add_data.html", istances=istances)