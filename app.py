import requests
import base64
import urllib.parse

from datetime import datetime, timedelta
from flask import Flask, jsonify, redirect, render_template, request, session


# Configure application
app = Flask(__name__)

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

    scope = 'user-read-private user-read-email'

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
                'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
            }
        }
    response = requests.post(TOKEN_URL, data=auth_options['data'], headers=auth_options['headers'])
    token_info = response.json()

    # token important data
    session['access'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    # when the token expires
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    
    #debug
    print(f"--------------------------------{session['access']}------------------{session['refresh_token']}------------------------{session['expires_at']}")
    
    #rediret to the main page
    return redirect('/success')

@app.route("/success")
def success():
    return "LOL"

