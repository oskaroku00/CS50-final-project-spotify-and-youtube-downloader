import requests
import base64
import urllib.parse

from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, session



# Configure application
app = Flask(__name__, static_url_path='/static')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug = True

app.secret_key = '8f42a73054b1749f8f58848be5e6502c'

# important variables 
CLIENT_ID = 'd5248a9df7094903900ac146b3fd8687'
CLIENT_SECRET = '464d694b440d4b308e64d3da16409b9f'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

#index of the app
@app.route("/")
def index():
    return "My spotify app. Log in to start: <a href='/login'>LOG IN<a>"

# redirecting the user to the login spotify page
@app.route("/login")
def login():

    scope = 'user-read-private playlist-read-private playlist-read-collaborative'

    # paramenter for the GET request
    parameters = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
    }
    # use the urllib to convert the parameters into query strings
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"

    # redirect to the authentification URL
    return redirect(auth_url)

#hadle the log in from spotify
@app.route('/callback')
def callback():
    # return if the user fails the authentification
    if 'error' in request.args:
        return jsonify(
            {"error": request.args['error']}
        )
    # user successfully authorized
    # sen a post request to potify
    # get the acces api token 
    if 'code' in request.args:
        # create the request body
        auth_options = {

            'url': 'https://accounts.spotify.com/api/token',
            'data': {
                'code': request.args['code'],
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            },
            'headers': {
                'content-type': 'application/x-www-form-urlencoded',
                #encode in base 64 the client id and secret id
                'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
            }
        }
    #send the request
    response = requests.post(TOKEN_URL, data=auth_options['data'], headers=auth_options['headers'])
    token_info = response.json()

    # token important data
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    # when the token expires
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']


    #rediret to the main page
    return redirect('/playlists')



#get playlist from user
@app.route("/playlists")
def get_playlists():
    #if the login went wrong
    if 'access_token' not in session:
        return redirect('/login')
    #if session expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    #request function
    from func import api_json
    
    playlists = api_json('me/playlists?limit=6')
    #get all the items I need fro the playlists
    
    images_url = []
    name = []
    tracks_href = [] 
    tracks_total = []
    playlist_range = playlists['total']
    for playlist in playlists['items']:
        for i in playlist['images']:
            if i['height'] == 300:
                images_url.append(i['url'])
        
        tracks_total.append(playlist['tracks']['href'])
        tracks_href.append(playlist['tracks']['total'])
        name.append(playlist['name'])

    return render_template('index.html', images_url=images_url, name=name, tracks_href=tracks_href, tracks_total=tracks_total, playlist_range=playlist_range)

#refreshes the token
@app.route('/refresh_token')
def refresh_token():
    #if the login went wrong
    if 'access_token' not in session:
        return redirect('/login')
    #if session expired
    if datetime.now().timestamp() > session['expires_at']:
        request_body = {

            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
        }

        request_header = {
            'content-type': 'application/x-www-form-urlencoded',
            #encode in base 64 the client id and secret id
            'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
        }
        #send the response
        response = requests.post(TOKEN_URL, data=request_body, headers=request_header)
        #set the new token request
        new_token_info = response.json()
        session['access_token'] = new_token_info['access_token']
        # when the token expires
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')

if __name__ == '__main__':
    app.run(debug=True)
