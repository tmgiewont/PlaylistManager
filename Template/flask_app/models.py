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

class Playlist(db.Document):
    pass

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    bio = db.StringField()
    favorites = db.ListField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Playlist(db.Document):
    author = db.ReferenceField(User, required=True)
    title = db.StringField(required=True, min_length=3, max_length=20)
    description = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    songs = db.ListField()
    profile_pic = db.ImageField()
    rate = db.FloatField(default=-1.0)

    meta = {'indexes': 
            [
                {'fields': ['$title', '$description'],
                'default_language' : 'english',
                'weights': {'title':10, 'description':2}
                }
            ]
            }

    def get_duration(self):
        tot = 0
        for s in self.songs:
            tot += s.duration
        return tot / 60

    

    

