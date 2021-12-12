from types import DynamicClassAttribute
from flask import Blueprint, render_template, url_for, redirect, request, flash
from app import playlist
from flask_login import current_user


playlist = Blueprint("playlist", __name__)
from .. import deezer_client
from ..forms import SearchForm, SearchSongForm, FavoritePlaylistForm, CreatePlaylistForm
from ..models import Playlist
from ..utils import current_time

import io
import base64

@playlist.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        print("HERE")
        return redirect(url_for("playlist.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)

@playlist.route("/create", methods=["GET", "POST"])
def create():
    form = CreatePlaylistForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        playlist = Playlist(
            author = current_user._get_current_object(),
            title = form.title.data,
            description = form.description.data,
            date = current_time(),
        )
        playlist.save()
        return redirect(request.path)

    return render_template("create_playlist.html", form=form)
    
    

@playlist.route("/playlist-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = Playlist.objects.search_text(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("playlist.index"))

    return render_template("playlistquery.html", results=results)

@playlist.route("/playlist/<curr_playlist>/song-results/<query>", methods=["GET"])
def song_results(curr_playlist, query):
    try:
        results = deezer_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("songs.index"))

    return render_template("query.html", results=results, playlist_id=curr_playlist)

#Displays playlist and gives user option to favorite
@playlist.route("/playlist/<playlist_id>", methods=["GET", "POST"])
def playlist_detail(playlist_id):
    try:
        playlist = Playlist.objects(id=playlist_id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("playlist.index"))

    count = len(playlist.songs)

    favorite = FavoritePlaylistForm()
    if favorite.validate_on_submit() and current_user.is_authenticated:
        user = current_user._get_current_object()
        user.favorites.append(playlist)
        user.save()
        return redirect(request.path)    
        
    return render_template("playlist_detail.html", playlist=playlist, favorite=favorite, count=count)

#Edit Playlist Add/Remove Songs, edit playlist title,bio, and picture
@playlist.route("/editplaylist/<playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id):

    playlist = Playlist.objects(id=playlist_id).first()

    if current_user.username != playlist.author:
        return redirect(url_for("playlist.index"))
    form = SearchSongForm()

    if form.validate_on_submit():
        return redirect(url_for("playlist.song_results", query=form.search_query.data, curr_playlist=playlist_id))

    return render_template("edit_playlist.html", form=form, playlist_id=playlist_id)

@playlist.route('/playlist/<playlist_id>/add/<song_id>/')
def add_song(playlist_id, song_id):
    song = deezer_client.retrieve_song_by_id(song_id)


    playlist = Playlist.objects(id=playlist_id).first()
    playlist.songs.append(vars(song))
    playlist.save()

    return redirect(url_for('playlist.edit_playlist', playlist_id=playlist_id))
