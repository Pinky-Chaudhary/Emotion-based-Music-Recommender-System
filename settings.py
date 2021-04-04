import os
REDIRECT_URI = os.environ['REDIRECT_URI']

# Client Keys
CLIENT_ID= os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# Scope for refrenced Spotify APIs
SCOPE = "user-top-read user-follow-read user-follow-modify playlist-modify-public playlist-modify-private user-read-recently-played"

# Spotify URL
SPOTIFY_AUTH_URL='https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL='https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL='https://api.spotify.com'
API_VERSION='v1'
SPOTIFY_API_URL='{}/{}'.format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
auth_query_parameters = {
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE,
    'client_id': CLIENT_ID
}
