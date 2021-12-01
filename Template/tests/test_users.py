from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"), 
    (
        ("", "password", "This field is required"),
        ("username", "",  "This field is required"),
        ("", "",  "This field is required"),
        ("Wrong", "test",  "Login failed. Check your username and/or password"),
        ("test", "Wrong",  "Login failed. Check your username and/or password"),
        ("wrong", "wrong",  "Login failed. Check your username and/or password")

    )
    )
def test_login_input_validation(auth, username, password, message):
    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login(username, password)
    assert str.encode(message) in resp.data


def test_logout(client, auth):
    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200
    
    resp = auth.logout()
    assert resp.status_code == 302



def test_change_username(client, auth):
    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200
    newUsername = "New"
    username = SimpleNamespace(username = newUsername, submit = "Update Username")
    form = UpdateUsernameForm(formdata=None, obj = username)
    resp = client.post("/account", data=form.data, follow_redirects=True)
    assert resp.status_code == 200
    resp = auth.login(newUsername)

    assert resp.status_code == 200
    with client:
        client.get("/")
        assert session["_user_id"] == newUsername

    user = User.objects.get(username=newUsername)
    assert newUsername == user["username"]


def test_change_username_taken(client, auth):
    newUsername = "taken"
    resp = auth.register(newUsername, "test2@gmail.com")
    assert resp.status_code == 200

    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200

    username = SimpleNamespace(username = newUsername, submit = "Update Username")
    form = UpdateUsernameForm(formdata=None, obj = username)
    resp = client.post("/account", data=form.data, follow_redirects=True)
    assert b"That username is already taken" in resp.data



@pytest.mark.parametrize(
    ("new_username","message"), 
    (
        ("","This field is required."),
        ("balls" * 20, "Field must be between 1 and 40 characters long.")
    )
)
def test_change_username_input_validation(client, auth, new_username, message):
    resp = auth.register()
    assert resp.status_code == 200

    resp = auth.login()
    assert resp.status_code == 200
    username = SimpleNamespace(username = new_username, submit = "Update Username")
    form = UpdateUsernameForm(formdata=None, obj = username)
    resp = client.post("/account", data=form.data, follow_redirects=True)

    assert str.encode(message) in resp.data
