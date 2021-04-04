import json
import requests
from flask import session
from random import shuffle
from spotify import *
from settings import *
from scipy import stats
import numpy as np
from model import User, Track, UserTrack
from views import db


def get_top_artists(auth_header, num_entities):
    """ Return list of new user's top and followed artists """
    artists = []
    term = ['long_term', 'medium_term']
    for length in term:
        playlist_api_endpoint = "{}/me/top/artists?time_range={}&limit={}".format(SPOTIFY_API_URL,length,num_entities)
        playlist_data = get_spotify_data(playlist_api_endpoint, auth_header)
        top_artists = playlist_data['items']
        for top_artist in top_artists:
            if top_artist['id'] not in artists:
                artists.append(top_artist['id'])

    users_followed_artists = f'{SPOTIFY_API_URL}/me/following?type=artist&limit={num_entities}'
    followed_artists_data = get_spotify_data(users_followed_artists, auth_header)
    followed_artists = followed_artists_data['artists']['items']
    for followed_artist in followed_artists:
        if followed_artist['id'] not in artists:
            artists.append(followed_artist['id'])

    return artists


def get_related_artists(auth_header, top_artists):
    """ Return list of related artists using users number one top artist """
    new_artists = []
    for artist_id in top_artists[:1]:
        request = "{}/artists/{}/related-artists".format(SPOTIFY_API_URL,artist_id)
        related_artists_data = get_spotify_data(request, auth_header)
        related_artists = related_artists_data['artists']

        for related_artist in related_artists:
            if related_artist['id'] not in new_artists:
                new_artists.append(related_artist['id'])
    return list(set(top_artists + new_artists))


def get_top_tracks(auth_header,artists):
    """ Return list containing 10 track ids per artist.    """
    top_tracks = []
    for artist_id in artists:
        request = "{}/artists/{}/top-tracks?market=from_token".format(SPOTIFY_API_URL, artist_id)
        track_data = get_spotify_data(request, auth_header)
        tracks = track_data['tracks']
        
        for track in tracks[:10]:
            print(track['is_playable'],type(track['is_playable']))
            if track['is_playable'] == True:
                track_uri = track['uri']
                track_id = track['id']
                track_name = track['name']
    
                track_exist = db.session.query(Track).filter(Track.uri == track_uri).all()
    
                if not track_exist:
                    new_track = Track(uri=track_uri, id=track_id, name=track_name)
                    db.session.add(new_track)
    
                user = session.get('user')
                new_user_track_exist = db.session.query(UserTrack).filter(UserTrack.user_id == user,
                                                                          UserTrack.track_uri == track_uri).all()
    
                if not new_user_track_exist:
                    new_user_track = UserTrack(user_id=user, track_uri=track_uri)
                    db.session.add(new_user_track)
    
                if track['id'] not in top_tracks:
                    top_tracks.append(track['id'])
        db.session.commit()

    return top_tracks


def cluster_ids(top_tracks, n=50):
    """ Return list of track ids clustered in groups of 50 """
    clustered_tracks = []
    for i in range(0, len(top_tracks), n):
        clustered_tracks.append(top_tracks[i:i + n])
    return clustered_tracks


def add_and_get_user_tracks(auth_header, clustered_tracks):
    """ Get two audio features for tracks:energy, valence.
    Add audio features to session .Return list of tracks associated with user.  """
    track_audio_features = []
    user_tracks =[]
    for track_ids in clustered_tracks:
        ids = '%2C'.join(track_ids)
        request = f'{SPOTIFY_API_URL}/audio-features?ids={ids}'
        audio_features_data = get_spotify_data(request, auth_header)
        audio_features = audio_features_data['audio_features']
        track_audio_features.append(audio_features)

    for tracks in track_audio_features:
        for track in tracks:
            if track:
                track_uri = track['uri']
                track_valence = track['valence']
                track_energy = track['energy']

                track_exist = db.session.query(Track).filter(Track.uri == track_uri).one()

                if track_exist:
                    track_exist.valence = track_valence
                    track_exist.energy = track_energy

        db.session.commit()

    no_audio_feats = db.session.query(Track).filter(Track.valence == None,Track.energy == None).all()
    for track in no_audio_feats:
        db.session.delete(track)
    db.session.commit()
    user_id = session.get('user')
    user = db.session.query(User).filter(User.id == user_id).one()
    user_tracks = user.tracks
    return user_tracks


def standardize_audio_features(user_tracks):
    """ Return dictionary of standardized audio features.
        Dict = Track Uri: {Audio Feature: Cumulative Distribution} """
    user_tracks_valence = list(map(lambda track: track.valence, user_tracks))
    valence_array = np.array(user_tracks_valence)
    valence_zscores = stats.zscore(valence_array)
    valence_zscores = valence_zscores.astype(dtype=float).tolist()
    valence_cdf = stats.norm.cdf(valence_zscores)

    user_tracks_energy = list(map(lambda track: track.energy, user_tracks))
    energy_array = np.array(user_tracks_energy)
    energy_zscores = stats.zscore(energy_array)
    energy_zscores = energy_zscores.astype(dtype=float).tolist()
    energy_cdf = stats.norm.cdf(energy_zscores)


    user_audio_features = {}
    for i, user_track in enumerate(user_tracks):
        user_audio_features[user_track.uri] = {'valence': valence_cdf[i], 'energy': energy_cdf[i] }

    return user_audio_features

def select_tracks(user_audio_features, mood):
    """ Return set of spotify track uri's to add to playlist based on mood. """
    selected_tracks = []
    emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"];

    for track, feature in user_audio_features.items():
        if emotions[mood] == "angry":
            if ((0 <= feature['valence'] <=0.25) and (0.5 <= feature['energy'] <= 0.75)):
                selected_tracks.append(track)
        if emotions[mood] =="disgust":
            if ((0<= feature['valence'] <= 0.25) and (0.25 <=feature['energy'] <= 0.5)):
                selected_tracks.append(track)
        if emotions[mood] =="fear":
            if ((0.10 <= feature['valence'] <= 0.35) and (0.75 <=feature['energy'] <= 0.90)):
                selected_tracks.append(track)
        if emotions[mood] =="happy":
            if ((0.5 <= feature['valence'] <= 1) and (0.5 <= feature['energy'] <= 0.75)):
                selected_tracks.append(track)
        if emotions[mood] =="neutral":
            if ((0.45 <= feature['valence'] <= 0.65) and (0.45 <= feature['energy'] <= 0.65)):
                selected_tracks.append(track)
        if emotions[mood] =="sad":
            if ((0.25 <= feature['valence'] <= 0.5) and (0 <= feature['energy'] <=0.25 )):
                selected_tracks.append(track)
        if emotions[mood] =="surprise":
            if ((0.5 <= feature['valence'] <= 0.75) and (0.75 <= feature['energy'] <=1)):
                selected_tracks.append(track)

    shuffle(selected_tracks)
    playlist_tracks = selected_tracks[:35]
    return set(playlist_tracks)

def recently_played(auth_header):
    playlist_tracks = []
    playlist_api_endpoint = "{}/me/playlists/".format(SPOTIFY_API_URL)
    playlist_data = get_spotify_data(playlist_api_endpoint, auth_header)
    playlist_tracks = playlist_data['items'][0]['id']
    return playlist_tracks



def create_playlist(auth_header, user_id, playlist_tracks, mood, playlist_name):
    """ Create playlist and add tracks to playlist. """
    name = f'{playlist_name}'
    payload = {
            'name': name,
            'description': 'Mood generated playlist'
    }
    playlist_request = f'{SPOTIFY_API_URL}/users/{user_id}/playlists'
    playlist_data = requests.post(playlist_request, data=json.dumps(payload), headers=auth_header).json()

    playlist_id = playlist_data['id']
    session['playlist'] = playlist_id

    track_uris = '%2C'.join(playlist_tracks)
    add_tracks = f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks?uris={track_uris}'
    tracks_added = post_spotify_data(add_tracks, auth_header)

    return playlist_id
