CLIENT_SIDE_URL='https://demo-spotify-api-user.herokuapp.com'
REDIRECT_URI = "{}/callback/".format(CLIENT_SIDE_URL)

# Client Keys
CLIENT_ID='aa6da89a8bdd44ffbe6d97d7460b6927'
CLIENT_SECRET='8c267a6ebc6b4500806cae0a3ecef2e3'

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
