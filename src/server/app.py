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



#create a flask instance
app = Flask(__name__)
#setting upload
app.config['UPLOADED_IMAGES_DEST'] = 'maps'
images_upload_set = UploadSet('images', IMAGES)
configure_uploads(app, images_upload_set)
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

    def __init__(self, name, msg_type, device_type, gps_lat, gps_long, timestamp, battery, ai_result_file):
        self.name = name
        self.msg_type = msg_type
        self.device_type = device_type
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.timestamp = timestamp
        self.battery = battery
        self.ai_result_file = ai_result_file

    def __repr__(self):
        return '<Name %r>' %self.names
#dictionary to list all object
objs_dict = {}

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
                         timestamp= dict_tele.get('timestamp'),
                         battery= dict_tele.get('battery'),
                         ai_result_file= dict_tele.get('imgname'))
    db.session.add(data)
    db.session.commit()
    #_________________________________decodifica immagine_______________________
    if dict_tele["msg_type"] == "ai_matching":
        # inserire decodifica e salvataggio immagine --> dati in dict_tele.get('img'))
        pass

    return str(data.id)

@app.route('/view_data', methods=['GET'])
def view_data():
    list_data=Db_data_model.query.order_by(Db_data_model.id.desc()).all()

    return render_template('view_data.html', instances=list_data)

#_______________________send direction to objs__________


@app.route('/get_direction/<obj_name>', methods=['GET'])
def send_direction(obj_name):   
    obj_name = obj_name
    if obj_name in objs_dict:
        objs_dict[obj_name] ["direction"][0] += 1
    else:
        objs_dict[obj_name] = {"direction": [1, 1], "steplenght": 1}

    return objs_dict[obj_name]
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


#________________main______________________________

if __name__ == '__main__':

    if True:  # first time (?)
        db.create_all()

    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)