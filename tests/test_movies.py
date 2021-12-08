from flask.wrappers import Response
import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    ("query", "message"),
    (
        ("", "This field is required"), 
        ("a", "Too many results"),
        ("BigFatCumShot", "Movie not found"),
        ("a" * 101,
        "Field must be between 1 and 100 characters long")
    )
    
)
def test_search_input_validation(client, query, message):
    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj = search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert str.encode(message) in response.data


def test_movie_review(client, auth):
    guardians_id = "tt2015381"
    url = f"/songs/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200

    letters = string.ascii_letters
    comment = ''.join(random.choice(letters) for i in range(10))
    review = SimpleNamespace(text = comment, submit = "Enter Comment")
    form = MovieReviewForm(formdata=None, obj = review)
    resp = client.post(url, data=form.data, follow_redirects=True)

    assert resp.status_code == 200

    resp = client.get(url)

    assert str.encode(comment) in resp.data

    review = Review.objects.get(content= comment)
    assert comment in review["content"]




@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("pp69", "Incorrect IMDb ID"),
        ("", "Incorrect IMDb ID"),
        ("peepoo420", "Incorrect IMDb ID"),
        ("peepeepoop420", "Incorrect IMDb ID")

    )
)
def test_movie_review_redirects(client, movie_id, message):
    url = f"/songs/{movie_id}"
    resp = client.get(url, follow_redirects=False)
    if len(movie_id)  == 0:
        assert resp.status_code == 404
    else:
        assert resp.status_code == 302
        resp = client.get(url, follow_redirects=True)
        assert resp.status_code == 200
        assert str.encode(message) in resp.data


@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("", "This field is required"),
        ("cum", "Field must be between 5 and 500 characters long."),
        ("cum" * 500, "Field must be between 5 and 500 characters long.")
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    url = f"/songs/tt2015381"

    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200

    review = SimpleNamespace(text = comment, submit = "Enter Comment")
    form = MovieReviewForm(formdata=None, obj = review)

    resp = client.post(url, data=form.data, follow_redirects=True)

    assert str.encode(message) in resp.data



