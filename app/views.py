import flask
from flask import render_template
from sqlalchemy import func, tuple_
from sqlalchemy.exc import SQLAlchemyError

from app import app
from functools import wraps
from flask import request, Response

from config import AUTH_LOGIN, AUTH_PASS, CASTLE
from app.types import *

MSG_UNDER_CONSTRUCTION = 'Страница находится в разработке'


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == AUTH_LOGIN and password == AUTH_PASS


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


if AUTH_PASS and AUTH_LOGIN:
    @app.route('/')
    @requires_auth
    def index():
        return render_template("index.html")
else:
    @app.route('/')
    def index():
        return render_template("index.html")


@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')


def get_squads():
    try:
        squads = Session().query(Squad).all()
        all_squads = []
        for squad in squads:
            all_squads.append(squad.squad_name)
        return all_squads
    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/users')
def get_usernames():
    try:
        session = Session()
        actual_profiles = session.query(Character.user_id, func.max(Character.date)).group_by(Character.user_id)
        profiles = actual_profiles.all()
        characters = session.query(Character, User).filter(tuple_(Character.user_id, Character.date)
                                                           .in_([(a[0], a[1]) for a in profiles]))\
            .join(User, User.id == Character.user_id)
        if CASTLE:
            characters = characters.filter(Character.castle == CASTLE)
        characters = characters.all()
        return render_template('users.html', characters=characters)
    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/player/<int:id>', methods=['GET'])
def get_user(id):
    session = Session()
    try:
        user = session.query(User).filter_by(id=id).first()
        return render_template('player.html', output=user)
    except SQLAlchemyError:
        Session.rollback()
        return flask.Response(status=400)


@app.route('/squads')
def squads_function():
    return render_template('squads.html', output=get_squads())


@app.route('/top')
def top():
    return render_template('top.html', output=MSG_UNDER_CONSTRUCTION)


@app.route('/build')
def build():
    return render_template('build.html', output=MSG_UNDER_CONSTRUCTION)


@app.route('/reports')
def reports():
    return render_template('reports.html', output=MSG_UNDER_CONSTRUCTION)


@app.route('/squad_craft')
def squad_craft():
    return render_template('squad_craft.html', output=MSG_UNDER_CONSTRUCTION)