from flask import Flask, render_template


#create a flask instance
app = Flask(__name__)

#Create a route decorator
@app.route('/')

def index():
    return "<h1>hello test"