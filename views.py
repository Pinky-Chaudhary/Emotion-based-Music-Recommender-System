import requests
from functools import wraps
import json
from flask import Flask, request, redirect, render_template, flash, session,jsonify
import datetime
from jinja2 import StrictUndefined
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.secret_key = os.environ['Secret_Key']
app.jinja_env.undefinded = StrictUndefined
db = SQLAlchemy(app)

from model import User, Track, UserTrack
import spotify,mood
from settings import *


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'access_token' not in session:
      return redirect('/')
    return f(*args, **kwargs)
  return decorated


@app.route('/')
def homepage():
    """ Render welcome page with login button """
    return render_template('homepage.html')


@app.route('/spotify-auth')
def authorization():
    """ Spotify Authorization Page """
    auth_url = spotify.get_user_authorization()
    return redirect(auth_url)

@app.route('/callback/')
def callback_handling():

    if 'access_token' not in session:
        response_data = spotify.get_tokens()
        session['access_token'] = response_data['access_token']
        session['refresh_token'] = response_data['refresh_token']        
        expires = datetime.datetime.now() + datetime.timedelta(seconds=response_data['expires_in'])
        session['access_token_expires'] = expires

        auth_header = spotify.get_auth_header(session.get('access_token'))
        username = spotify.get_user_id(auth_header)
        session['user'] = username
        user = db.session.query(User).filter(User.id == username).all()
        if not user:
            new_user = User(id=username, refresh_token=response_data['refresh_token'])
            db.session.add(new_user)
            db.session.commit()

    elif session['access_token_expires'] < datetime.datetime.now():
        response_data = spotify.get_refreshed_token()
        session['access_token'] = response_data['access_token']
        expires = datetime.datetime.now() + datetime.timedelta(seconds=response_data['expires_in'])
        session['access_token_expires'] = expires
    return redirect('/mood')



@app.route('/about')
def about():
    """ About page with description about app """
    return render_template('about.html')

  
  
@app.route('/mood')
@requires_auth
def get_user_mood():
    """ Get user's current mood.
    Add User to database and save user's artists to session. """
    auth_header = spotify.get_auth_header(session.get('access_token'))
    top_artists = mood.get_top_artists(auth_header, 25)
    # if user is new thier aill be no new data based on previous activtiy
    if len(top_artists) == 0:
        top_artists = mood.get_artists_for_new_user(auth_header)

    artists = mood.get_related_artists(auth_header, top_artists)
    session['artists'] = artists
    return render_template('main.html')

  
  
@app.route('/camera')
@requires_auth
def open_camera():
    return render_template('mood.html')

  
  
@app.route('/playlist')
@requires_auth
def playlist_created():
    """ Create playlist """
    token = session.get('access_token')
    username = session.get('user')
    auth_header = spotify.get_auth_header(token)
    name = request.args.get('name')
    user_mood = int(request.args.get('mood'))
    session['name'] = name

    user = db.session.query(User).filter(User.id == username).one()
    user_tracks = user.tracks

    if not user_tracks:
        try:
            user_artists = session.get('artists')
        finally:
            top_tracks = mood.get_top_tracks(auth_header, user_artists)
            cluster = mood.cluster_ids(top_tracks)
            user_tracks = mood.add_and_get_user_tracks(auth_header, cluster)

    audio_feat = mood.standardize_audio_features(user_tracks)
    playlist_tracks = mood.select_tracks(audio_feat, user_mood)
    playlist_id = mood.create_playlist(auth_header, username, playlist_tracks, user_mood, name)

    playlist_data = mood.get_track_detail_from_playlist(auth_header,playlist_id)
    session['spotify'] = playlist_id
    playlist_iframe_href = "https://open.spotify.com/embed/playlist/" + playlist_id
    return render_template('playlist.html', playlist_iframe_href=playlist_iframe_href,header="Generated Playlist",playlist =playlist_data )

  
  
@app.route('/playlist-created')
@requires_auth
def playlist_created_by_user():
    """ Create playlist """
    token = session.get('access_token')
    auth_header = spotify.get_auth_header(token)
    playlist = mood.recently_played(auth_header)
    return render_template('recent_playlist.html', playlist = playlist, header="Your Top Playlist")

@app.route('/logout')
def logout():

    """ Logged out and session cleared """
    username = session.get('user')
    user_track_exist = db.session.query(UserTrack).filter(UserTrack.user_id == username).all()
    for user_track in user_track_exist:
        db.session.delete(user_track)
    db.session.commit()
    users= db.session.query(User).filter(User.id == username).all()
    for user in users :
        db.session.delete(user)
    db.session.commit()
    
    session.clear()
    return redirect('/')
  
