from asyncio.windows_events import NULL
from pathlib import Path
import sys
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import  FileField
from flask_wtf.file import FileRequired, FileAllowed , FileField


from flask_sqlalchemy import SQLAlchemy



#create a flask instance
app = Flask(__name__)
#Key for forms
app.config['SECRET_KEY'] = "password" #In teoria andrebbe nascosta TODO capire se implementare sicurezza
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
    id =        db.Column(db.Integer, nullable=False, primary_key=True)
    name =      db.Column(db.String,  nullable=False)
    type =      db.Column(db.String,  nullable=False)
    gps_lat =   db.Column(db.Integer, nullable=False)
    gps_long =  db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer)
    battery =   db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' %self.names


#Create a route decorator
@app.route('/')

def index():
    return render_template("index.html")


@app.route('/data/add', methods=['GET', 'POST'])

def add_data():
    data = Db_data_model(name= "1", type = "team", gps_lat = 12, gps_long = 145,)
    db.session.add(data)
    db.session.commit()
    istances = Db_data_model.query.order_by(Db_data_model.name)
    
    return render_template("add_data.html", istances=istances)
 
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


#Error pages

#Invalid page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500