import json
import requests
import base64
import urllib
from settings import *
from flask import request, session

def get_user_authorization():
    """ Return user authorization url. """

    url_args = '&'.join(['{}={}'.format(key, urllib.parse.quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = '{}/?{}'.format(SPOTIFY_AUTH_URL, url_args)
    session['count'] = 0
    return auth_url


def get_tokens():
    """ Return authorization tokens from Spotify """

    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    try:
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    except:
        # Some error with *your* request, not Spotify
        current_app.logger.error("Spotify client failed")
        raise
    else:
        response_data = json.loads(post_request.text)
    return response_data

def get_refreshed_token():

    token_data = {
        "grant_type":'refresh_token',
        "refresh_token":session['refresh_token']
    }
    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    token_headers = {"Authorization": f"Basic {client_creds_b64.decode()}"}
    r = requests.post(SPOTIFY_TOKEN_URL, data=token_data, headers=token_headers)
    return json.loads(r.text)


def get_auth_header(access_token):
    """ Return authorization header which will be used to access Spotify API """
    auth_header = {'Authorization': 'Bearer {}'.format(access_token)}
    return auth_header


def get_user_id(auth_header):
    """ Return users spotify id to add to database """

    # Get user id
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=auth_header)
    profile_data = json.loads(profile_response.text)
    return profile_data['id']


def get_spotify_data(request, auth_header):
    """ Return data from Spotify get request with error handling """

    data = requests.get(request, headers=auth_header)
    if data.status_code == 200:
        data = data.json()

    elif data.status_code == 401:
        response_data = get_refreshed_token()
        session['access_token'] = response_data['access_token']
        get_spotify_data(request, auth_header)

    return data


def post_spotify_data(request, auth_header):
    """ Return data from Spotify post request with error handling. """

    data = requests.post(request, headers=auth_header)

    if data.status_code == 200:
        data = data.json()

    elif data.status_code == 401:
        response_data = get_refreshed_token()
        session['access_token'] = response_data['access_token']
        get_spotify_data(request, auth_header)
    return data