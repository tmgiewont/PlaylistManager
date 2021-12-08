from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import deezer_client
from ..forms import MovieReviewForm, SearchForm
from ..models import User
from ..utils import current_time

songs = Blueprint("songs", __name__)

# @songs.route("/", methods=["GET", "POST"])
# def index():
#     form = SearchForm()

#     if form.validate_on_submit():
#         return redirect(url_for("songs.query_results", query=form.search_query.data))

#     return render_template("index.html", form=form)


@songs.route("/song-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = deezer_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("songs.index"))

    return render_template("query.html", results=results)


# @songs.route("/songs/<song_id>", methods=["GET", "POST"])
# def song_detail(song_id):
#     try:
#         result = deezer_client.retrieve_song_by_id(song_id)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("users.login"))

#     form = MovieReviewForm()
#     if form.validate_on_submit() and current_user.is_authenticated:
#         review = Review(
#             commenter=current_user._get_current_object(),
#             content=form.text.data,
#             date=current_time(),
#             imdb_id=movie_id,
#             movie_title=result.title,
#         )
#         review.save()

#         return redirect(request.path)

#     reviews = Review.objects(imdb_id=movie_id)

#     return render_template(
#         "movie_detail.html", form=form, movie=result, reviews=reviews
#     )


@songs.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)
