from requests.models import RequestField
from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    bio = db.StringField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    playlist = db.ReferenceField(Playlist, required=True)
    content = db.StringField(required=True, max_length=500, min_length=5)
    date = db.StringField(required=True)

class Playlist(db.Document):
    author = db.ReferenceField(User, required=True)
    title = db.StringField(required=True, min_length=3, max_length=20)
    description = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    songs = db.ListField()
    reviews = db.ListField(db.ReferenceField(Review))


