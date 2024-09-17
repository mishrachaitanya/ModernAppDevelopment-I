from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship,session
import app
import os
from flask import Flask
app=app.app
current_dir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,'database_bloglite.sqlite3')

db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

from flask_login import LoginManager, UserMixin
# login=LoginManager()
# login.login_view='controllers.homepage'
# login.init_app(app)


class User(db.Model, UserMixin):
    __tablename__='user'
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    first_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String)
    profile_photo=db.Column(db.BLOB)
    mimetype=db.Column(db.String)
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    #dob=db.Column(db.String, nullable=False)
    
    #User can have many blogs/posts
    post=db.relationship('Blogs', backref='user')

    #User can have many followers/followings
    foll=db.relationship('User_info', backref='user')

    def get_id(self):
        return str(self.username)
        

# @login.user_loader
# def load_user(username):
#     return User.query.get(username)

class User_info(db.Model):
    __tablename__='user_info'
    info_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    followers=db.Column(db.String)
    following=db.Column(db.String)
    username=db.Column(db.String, db.ForeignKey('user.username', ondelete='cascade'))


class Blogs(db.Model):
    __tablename__='blogs'
    blogid=db.Column(db.Integer, primary_key=True,autoincrement=True)
    title=db.Column(db.String)
    caption=db.Column(db.String)
    image=db.Column(db.BLOB)
    time=db.Column(db.String)
    username=db.Column(db.String,db.ForeignKey('user.username',ondelete='cascade'), nullable=False)
    mimetype=db.Column(db.String)
    posts=db.relationship('Posts', backref='blogs')


class Posts(db.Model):
    __tablename__='posts'
    post_id=db.Column(db.Integer, db.ForeignKey('blogs.blogid',ondelete='cascade') )
    comment=db.Column(db.String)
    likes=db.Column(db.String)
    author=db.Column(db.String, nullable=False)
    pid=db.Column(db.Integer, primary_key=True, autoincrement=True)

class User_search(db.Model):
    __tablename__='user_search'
    rowid=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String)
    last_name=db.Column(db.String)
    username=db.Column(db.String)
    
db.create_all()


