from types import DynamicClassAttribute
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_app import playlist
from flask_login import current_user


playlist = Blueprint("playlist", __name__)
from .. import deezer_client
from ..forms import MovieReviewForm, SearchForm, FavoritePlaylistForm, CreatePlaylistForm
from ..models import Playlist, User
from ..utils import current_time

import io
import base64

@playlist.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
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
    
    

@playlist.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = Playlist.objects.search_text(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("playlist.index"))

    return render_template("playlistquery.html", results=results)

#Displays playlist and gives user option to favorite
@playlist.route("/playlist/<playlist_id>", methods=["GET", "POST"])
def playlist_detail(playlist_id):
    try:
        playlist = Playlist.objects(id=playlist_id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("playlist.index"))

    img = get_b64_img(playlist)

    form = FavoritePlaylistForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        user = current_user._get_current_object()
        user.favorites.append(playlist)
        user.save()
        return redirect(request.path)
        
    return render_template("playlist_detail.html", playlist=playlist, image=img, form=form)

#Edit Playlist Add/Remove Songs, edit playlist title,bio, and picture
@playlist.route("/editplaylist/<playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id):
    try:
        playlist = Playlist.objects(id=playlist_id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("playlist.index"))

    form = MovieReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title,
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    return render_template(
        "movie_detail.html", form=form, movie=result, reviews=reviews
    )


def get_b64_img(playlist):
    bytes_im = io.BytesIO(playlist.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image