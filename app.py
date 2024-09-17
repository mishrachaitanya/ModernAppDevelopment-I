from flask import Flask
from flask_restful import Api

import os

app=Flask(__name__, template_folder='templates')
#api=Api(app)
app.app_context().push()

app.config['SECRET_KEY']='jhuig8976hDSFSD#!@'

from controllers import *
from models import *


current_dir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,'database_bloglite.sqlite3')

db=SQLAlchemy()
db.init_app(app)
if __name__=="__main__":
        db.create_all()
        app.run(debug=True,port=5600)