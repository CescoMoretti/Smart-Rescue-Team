import math
import os
from asyncio.windows_events import NULL
from pathlib import Path
import sys

from sqlalchemy import false
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

import json
from find_unexplored_space import find_unexplored_space
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import  FileField
from flask_wtf.file import FileRequired, FileAllowed , FileField

import base64
import cv2

from flask_sqlalchemy import SQLAlchemy

import pandas as pd
import folium
from folium import plugins
import numpy as np

from turbo_flask import Turbo
import threading
import time
from threading import Lock
import random


#create a flask instance
app = Flask(__name__)


this_path = os.getcwd()
#Key for forms
app.config['SECRET_KEY'] = "password" #In teoria andrebbe nascosta TODO capire se implementare sicurezza
#setting upload
app.config['UPLOADED_IMAGES_DEST'] = 'maps'
images_upload_set = UploadSet('images', IMAGES)
configure_uploads(app, images_upload_set)

app.config['TEMPLATES_AUTO_RELOAD'] = True
turbo = Turbo(app)
app.config['SERVER_NAME'] = "127.0.0.1:5000"

#detection image id
detected_img_istance = None
flag_match = False
mutex = Lock()
#dictionary to list all object
objs_dict = {}
time_direction_calc = time.time()
image_used = []
image_id = 0

#Create form class
class Image_form(FlaskForm):
    #name = StringField('Name', validators=[DataRequired()])
    image = FileField('Map', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

print(this_path)



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
    global detected_img_istance
    global objs_dict
    global mutex
    global flag_match 

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
    
    with mutex:
        db.session.add(data)
        db.session.commit()
    
    #_________________________________decodifica immagine_______________________
    if flag_match == False:
        if dict_tele["msg_type"] == "ai_matching":

            if dict_tele['ack'] == True:
                f = json.loads(request.data)
                jpg_original = base64.b64decode(f['image'])
                jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                img = cv2.imdecode(jpg_as_np, flags=1)
                cv2.imwrite(this_path+'/static/predicted_imgs/positive/'+str(dict_tele['imgname'])+'.jpg', img)
                detected_img_istance = dict_tele
                flag_match = True

            else:
                f = json.loads(request.data)
                jpg_original = base64.b64decode(f['image'])
                jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                img = cv2.imdecode(jpg_as_np, 1)
                cv2.imwrite(this_path+'/static/predicted_imgs/negative/'+str(dict_tele['imgname'])+'.jpg', img)
    

    #____________________riempimento dizionario per la scelta della direzione______
    if dict_tele["device_type"] == "team": #type of object that can be controlled
        if dict_tele['name'] not in objs_dict: #if not exist in dictionary
            #TODO set direction in a smarter way
            r = lambda: random.randint(100, 255)
            color = ('#%02X%02X%02X' % (r(), r(), r()))
            objs_dict[dict_tele['name']] = {"last_lat": 0, "last_long": 0, "distance": 0, "direction": [1,1], "step_lenght": 0.0005, 'color': color}
        
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
    global mutex
    global flag_match
    global detected_img_istance
    #take extra simboles out    
    obj_name = obj_name.replace("<", "")
    obj_name = obj_name.replace(">", "") 
    if flag_match == False:
        if time.time() - time_direction_calc >= 10.0:
            df = pd.read_sql(Db_data_model.query.statement, Db_data_model.query.session.bind)
            #print(df)
            objective_point = find_unexplored_space(df)
            #print(objective_point)
            df_team = pd.DataFrame.from_dict(objs_dict)
            df_team = df_team.T
            #print(df_team)
            for index, row in df_team.iterrows():
                ilat = row['last_lat']
                ilong = row['last_long']
                #row['distance'] = row[['last_lat', 'last_long']].sub(np.array(objective_point)).pow(2).sum(1).pow(0.5)
                row['distance'] = math.hypot(ilong - objective_point[1], ilat - objective_point[0])
            print(df_team)
            print(objs_dict)
            df_team['distance'] = pd.to_numeric(df_team['distance'])
            print(type(df_team))
            nearest_obj = df_team['distance'].idxmin()
            #print(nearest_obj)
            #nearest_obj= df_team.iloc[[id]]
            objs_dict[nearest_obj]["direction"] = [objective_point[0] - objs_dict[nearest_obj]["last_lat"],
                                                    objective_point[1] - objs_dict[nearest_obj]["last_long"]]

            Db_data_model.query.filter_by(name=nearest_obj, msg_type="new_direction").delete()
            mutex.acquire()
            db.session.commit()
            mutex.release()
            data = Db_data_model(name=nearest_obj,
                                msg_type='new_direction',
                                device_type=objs_dict[nearest_obj]['color'],
                                gps_lat=objective_point[0],
                                gps_long=objective_point[1],
                                timestamp=time.time(),
                                battery = "",
                                ai_result_file = "",
                                ai_result_ack = "")
            mutex.acquire()
            db.session.add(data)
            db.session.commit()
            mutex.release()

            time_direction_calc = time.time()

           
        if obj_name in objs_dict:
            
            direction = {"last_lat": objs_dict[obj_name]["last_lat"],
                        "last_long": objs_dict[obj_name]["last_long"],
                        "direction": objs_dict[obj_name]["direction"],
                        "step_lenght": objs_dict[obj_name]["step_lenght"]}        
        else:
            direction = {"last_lat": None, "last_long": None, "direction": [1, 1], "step_lenght": 0.0001}

    else:
        print("match trovato mando tutti li")
        objs_dict[obj_name]["direction"] = [detected_img_istance['gps']['lat']- objs_dict[obj_name]["last_lat"],
                           detected_img_istance['gps']['long']- objs_dict[obj_name]["last_long"]]
        direction = {"last_lat": objs_dict[obj_name]["last_lat"],
                        "last_long": objs_dict[obj_name]["last_long"],
                        "direction": objs_dict[obj_name]["direction"],
                        "step_lenght": objs_dict[obj_name]["step_lenght"]}  
    return direction 

#_______________________________visualize the map______________________________
@app.route('/view_map', methods=['GET'])
def view_map():
    filename_img = '/static/predicted_imgs/positive/example.jpg'
    return render_template('view_map.html', file_name = filename_img)

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
            time.sleep(5)
            turbo.push(turbo.replace(render_template('just_map.html'), 'load'))
            #turbo.push(turbo.replace(render_template('just_img.html'), 'img_load'))

@app.context_processor
def create_map():
    global mutex
    with mutex:
        df = pd.read_sql(Db_data_model.query.statement, Db_data_model.query.session.bind)

        telemetry_data = df[df['msg_type']=='telemetry']
        map = folium.Map(location=telemetry_data[['gps_lat', 'gps_long']].mean().values, zoom_start=13)
        folium.plugins.HeatMap(telemetry_data[['gps_lat', 'gps_long']].values).add_to(map)

        # ML_df = df[df['msg_type'] == 'ai_result']
        # ML_df = ML_df[ML_df['ai_result_ack'] == 'True']
        # for i in range(0, len(ML_df)):
        #     folium.Marker(
        #         location=[ML_df.iloc[i]['gps_lat'], ML_df.iloc[i]['gps_long']],
        #         popup=ML_df.iloc[i]['name'],
        #     ).add_to(map)

        # direction_df = df[df['msg_type'] == 'new_direction']
        # for i in range(0, len(direction_df)):
        #     folium.Marker(
        #         location=[direction_df.iloc[i]['gps_lat'], direction_df.iloc[i]['gps_long']],
        #         popup=direction_df.iloc[i]['name'],
        #         icon=folium.Icon(icon="glyphicon glyphicon-search", color='black', icon_color=direction_df.iloc[i]['device_type'])
        #     ).add_to(map)

        new_map_name = "map" + str(time.time()) + ".html"
        map.save('static/' + new_map_name)

        global image_used
        global image_id
        if image_id>2:
            image_used.pop(1)
        image_used.append(new_map_name)
        image_id+=1

        for filename in os.listdir('static/'):
            if (filename.startswith('map') and filename not in image_used):
                #print('static/' + filename)
                os.remove('static/' + filename)

    #--------updating img----------
        global detected_img_istance
        filename_img = 'static/predicted_imgs/positive/example.jpg'
        if detected_img_istance != None:
            filename_img = 'static/predicted_imgs/positive/'+str(detected_img_istance['imgname'])+'.jpg'

        return {'map_name': new_map_name, 'file_name': filename_img}


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