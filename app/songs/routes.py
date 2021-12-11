from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import deezer_client
from ..forms import SearchForm
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
