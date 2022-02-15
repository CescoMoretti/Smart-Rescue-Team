import os
from asyncio.windows_events import NULL
from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import json
from find_unexplored_space import find_unexplored_space
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import  FileField
from flask_wtf.file import FileRequired, FileAllowed , FileField



from flask_sqlalchemy import SQLAlchemy

import pandas as pd
import folium
from folium import plugins
import numpy as np

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
app.config['SERVER_NAME'] = "127.0.0.1:5000"

#dictionary to list all object
objs_dict = {}
time_direction_calc = time.time()
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
    ai_result_file =db.Column(db.String)
    ai_result_ack = db.Column(db.String)

    def __init__(self, name, msg_type, device_type, gps_lat, gps_long, timestamp, battery, ai_result_file, ai_result_ack):
        self.name = name
        self.msg_type = msg_type
        self.device_type = device_type
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.timestamp = timestamp
        self.battery = battery
        self.ai_result_file = ai_result_file
        self.ai_result_ack = ai_result_ack

    def __repr__(self):
        return '<Name %r>' %self.names


#Create a route decorator
@app.route('/')
def index():
    return render_template("index.html")

#__________________________________add data_____________________
@app.route('/data/add/<json_string>', methods=['POST'])
def add_data(json_string):
    global objs_dict
    #_________________________________inserimento dati db________________________
    dict_tele = json.loads(json_string)
    data = Db_data_model(name= dict_tele['name'],
                         msg_type = dict_tele["msg_type"],
                         device_type = dict_tele["device_type"],
                         gps_lat = dict_tele['gps']['lat'],
                         gps_long = dict_tele['gps']['long'],
                         timestamp= dict_tele.get('timestamp'),
                         battery= dict_tele.get('battery'),
                         ai_result_file= dict_tele.get('imgname'),
                         ai_result_ack = dict_tele.get('ack'))
    db.session.add(data)
    db.session.commit()
    #_________________________________decodifica immagine_______________________
    if dict_tele["msg_type"] == "ai_matching":
        # inserire decodifica e salvataggio immagine
        pass
    
    

    #____________________riempimento dizionario per la scelta della direzione______
    if dict_tele["device_type"] == "team": #type of object that can be controlled
        if dict_tele['name'] not in objs_dict: #if not exist in dictionary
            #TODO set direction in a smarter way 
            objs_dict[dict_tele['name']] = {"last_lat": 0, "last_long": 0, "direction": [1,1], "steplenght": 0.0001} 
        
        if dict_tele["msg_type"] == "telemetry":
            objs_dict[dict_tele['name']]["last_lat"] = dict_tele['gps']['lat']
            objs_dict[dict_tele['name']]["last_long"] = dict_tele['gps']['long']
    
    return str(data.id)

@app.route('/view_data', methods=['GET'])
def view_data():
    list_data=Db_data_model.query.order_by(Db_data_model.id.desc()).all()

    return render_template('view_data.html', instances=list_data)

#_______________________send direction to objs_____________________________________

@app.route('/get_direction/<obj_name>', methods=['GET'])
def send_direction(obj_name): 
    global time_direction_calc
    print(time_direction_calc)
    print("brake 1")
    if time.time() - time_direction_calc >= 10.0:
        print("brake 2")
        df = pd.read_sql(Db_data_model.query.statement, Db_data_model.query.session.bind)
        print(df)
        objective_point = find_unexplored_space(df)
        df_team = pd.DataFrame.from_dict(objs_dict)
        for item in df_team:
            df_team[item] ['distance'] = df_team[item][['lat', 'long']].sub(np.array(objective_point)).pow(2).sum(1).pow(0.5)
        id = df_team['distance'].idmin()
        nearest_obj= df_team.iloc[[id]]
        objs_dict[nearest_obj]["direction"] = [objs_dict[nearest_obj]["last_lat"] - objective_point[0],
                                               objs_dict[nearest_obj]["last_long"] - objective_point[1]] 
        time_direction_calc = time.time()
    
    #take extra simboles out    
    obj_name = obj_name.replace("<", "")
    obj_name = obj_name.replace(">", "")    
    if obj_name in objs_dict:
        
        direction = objs_dict[obj_name]        
    else:
        direction = {"last_lat": None, "last_long": None, "direction": [1, 1], "steplenght": 0.0001}        

    return direction # {key: objs_dict[obj_name][key] for key in objs_dict[obj_name].keys() & {'direction', 'steplenght'}}

#_______________________________visualize the map______________________________
@app.route('/view_map', methods=['GET'])
def view_map():
    
    return render_template('view_map.html')

#_______________________________________add map manualy_________________________ 
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
            #print('static/' + filename)
            os.remove('static/' + filename)

    m.save('static/' + new_map_name)

    return {'map_name': new_map_name}


#______________________________route to stop icon error_______________
@app.route("/favicon.ico")
def favicon():
    return "", 200
#____________________________main______________________________

if __name__ == '__main__':

    if True:  # first time (?)
        db.create_all()

    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)