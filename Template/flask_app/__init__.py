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

# stdlib
from datetime import datetime
import os

from flask_app import users

# local
from .client import DeezerClient


db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
deezer_client = DeezerClient()

#from .routes import main
from .users.routes import users
from .songs.routes import songs

def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    #app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(songs)

    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
