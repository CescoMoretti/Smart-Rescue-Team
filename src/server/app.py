import os
from asyncio.windows_events import NULL
from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import json
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import  FileField
from flask_wtf.file import FileRequired, FileAllowed , FileField


from flask_sqlalchemy import SQLAlchemy

import pandas as pd
import folium
from folium import plugins

from turbo_flask import Turbo
import threading
import time



#create a flask instance
app = Flask(__name__)
#Key for forms
app.config['SECRET_KEY'] = "password" #In teoria andrebbe nascosta TODO capire se implementare sicurezza
#setting upload
app.config['UPLOADED_IMAGES_DEST'] = 'maps'
images_upload_set = UploadSet('images', IMAGES)
configure_uploads(app, images_upload_set)

app.config['TEMPLATES_AUTO_RELOAD'] = True
turbo = Turbo(app)
app.config['SERVER_NAME'] = "192.168.1.75:80"

#Create form class
class Image_form(FlaskForm):
    #name = StringField('Name', validators=[DataRequired()])
    image = FileField('Map', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])


#App database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
#Initialize database
db = SQLAlchemy(app)
#Create data model
class Db_data_model(db.Model):
    id =          db.Column(db.Integer, nullable=False, primary_key=True)
    name =        db.Column(db.String,  nullable=False)
    msg_type =    db.Column(db.String,  nullable=False)
    device_type = db.Column(db.String,  nullable=False)
    gps_lat =     db.Column(db.Integer, nullable=False)
    gps_long =    db.Column(db.Integer, nullable=False)
    timestamp =   db.Column(db.Integer)
    battery =     db.Column(db.Integer)

    def __init__(self, name, msg_type, device_type, gps_lat, gps_long, timestamp, battery):
        self.name = name
        self.msg_type = msg_type
        self.device_type = device_type
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.timestamp = timestamp
        self.battery = battery

    def __repr__(self):
        return '<Name %r>' %self.names


#Create a route decorator
@app.route('/')

def index():
    return render_template("index.html")


@app.route('/data/add/<json_string>', methods=['POST'])
def add_data(json_string):
    dict_tele = json.loads(json_string)
    data = Db_data_model(name= dict_tele['name'],
                         msg_type = dict_tele["msg_type"],
                         device_type = dict_tele["device_type"],
                         gps_lat = dict_tele['gps']['lat'],
                         gps_long = dict_tele['gps']['long'],
                         timestamp= dict_tele['timestamp'],
                         battery= dict_tele['battery'])
    db.session.add(data)
    db.session.commit()     
    return str(data.id)

@app.route('/view_data', methods=['GET'])
def view_data():
    list_data=Db_data_model.query.order_by(Db_data_model.id.desc()).all()

    return render_template('view_data.html', instances=list_data)


@app.route('/view_map', methods=['GET'])
def view_map():
    return render_template('view_map.html')

 
@app.route('/images', methods=['GET', 'POST'])
def add_image():  
    path_map = None
    image = None
    filename = None
    form = Image_form()
    if form.validate_on_submit():
        filename = images_upload_set.save(form.image.data)
        path_map = images_upload_set.path(filename)
        image = filename  
    return render_template("images.html",
                            filename = filename,     
                            path_map = path_map,
                            image = image,
                            form = form)


#_______________Error pages_________________________________

#Invalid page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

#________________Turbo flask setting__________________

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        while True:
            time.sleep(10)
            turbo.push(turbo.replace(render_template('just_map.html'), 'load'))

@app.context_processor
def create_map():
    df = pd.read_sql(Db_data_model.query.statement, Db_data_model.query.session.bind)
    m = folium.Map([44.847343, 10.722371], zoom_start=13)
    stationArr = df[['gps_lat', 'gps_long']].values
    m.add_child(plugins.HeatMap(stationArr, radius=15))

    new_map_name = "map" + str(time.time()) + ".html"

    for filename in os.listdir('static/'):
        if (filename.startswith('map')):
            print('static/' + filename)
            os.remove('static/' + filename)

    m.save('static/' + new_map_name)

    return {'map_name': new_map_name}


#________________main______________________________

if __name__ == '__main__':

    if True:  # first time (?)
        db.create_all()

    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)