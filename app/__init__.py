# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message# stdlib
from datetime import datetime
import os

from app import users

# local
from .client import DeezerClient


db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
deezer_client = DeezerClient()
mail = Mail()
#from .routes import main
from .users.routes import users
from .playlist.routes import playlist
from .songs.routes import songs

def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    #app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    #app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(songs)
    app.register_blueprint(playlist)
    

    app.config["SECRET_KEY"] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'
    app.config["MONGODB_HOST"] = os.getenv('MONGODB_HOST')
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_SENDER'] = "noreply@gmail.com"
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True


    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    mail.init_app(app)
    #global mail
    #mail = Mail(app)

    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
