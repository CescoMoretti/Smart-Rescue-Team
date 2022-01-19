from server.app import db

class Db_data_model(db.Model):
    id =        db.Column(db.Integer, nullable=False, unique=True)
    type =      db.Column(db.String, nullable=False)
    gps_lat =   db.Column(db.Integer, nullable=False)
    gps_long =  db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Datetime, nullable=False)
    battery =   db.Column(db.Integer)