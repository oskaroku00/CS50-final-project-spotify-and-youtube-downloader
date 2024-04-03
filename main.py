import requests
import base64
import urllib.parse
import os
from datetime import datetime
import shutil
from flask import Flask, jsonify, redirect, render_template, request, session, flash, send_file



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
    return render_template("youtube.html")

#if the user only wonts to download 1 track without login and usig a URL
@app.route('/youtube', methods=["GET", "POST"])
def youtube():
    from func import get_song_url
    if request.method == "POST":
        
        url = request.form.get('url')

        video = get_song_url(url)
        #error cases
        if video == 1:
            flash('Invalid URL')
            return render_template('youtube.html') 
        if video == 2:
            flash("Couldn't download, or invalid URL")
            return render_template('youtube.html')
        else:
            return send_file(f'downloaded/{video}.mp3', as_attachment=True)

        
    else: 
        #remove all the files in the downloaded directory to create space
        shutil.rmtree('/home/oskar/project/downloaded')
        os.makedirs('downloaded')
        return render_template('youtube.html')

@app.route('/spotify_uri', methods=["GET", "POST"])
def spotify_uri():
    #if the login went wrong
    if 'access_token' not in session:
        return redirect('/login')
    #if session expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    from func import get_song, api_json
    if request.method == "POST":
        
        url = request.form.get('url')
        #get the valid id for the list
        try:
            uri = url.split("spotify:playlist:", 1)[1]
        except IndexError:
            try:
                url = url.split("https://open.spotify.com/playlist/", 1)[1]
            except IndexError:
                flash('Invalid URI')
                return render_template('spotify_uri.html')
        uri = ""
        c = 0
        for i in url:
            if i != "?":
                c += 1
            else:
                uri = url[0:c]
                break

        
        #playlist request 
        print(uri)
        playlist = api_json(f'playlists/{uri}/tracks?limit=50')

        #name of the playlist
        pl_n = api_json(f'playlists/{uri}')
        
        playlist_name = pl_n['name']

        
        tracks_total = playlist['total']
        name = []
        artist = []

        for i in playlist['items']:
            name.append(i['track']['name'])
            for b in i['track']['artists']:
                if b['name'] == "":
                    artist.append("null")
                else:
                    artist.append(b['name'])
                
        
        #create a path where to store the songs
        
        path_name = playlist_name
        path = f'/home/oskar/project/downloaded/{path_name}'
        os.mkdir(path)
        #counter of songs downloaded
        
        counter = 1
        if tracks_total > 50:
            tracks_total == 50
        for i in range(tracks_total):
            get_song(name[i], path_name)
            
            # x = counter/tracks_total * 100

            # progress(int(x))
            # counter += 1

        
        shutil.make_archive(f'{path_name}', 'zip', f'/home/oskar/project/downloaded/{path_name}')
        
        shutil.move(f'{path_name}.zip', '/home/oskar/project/downloaded')
        
        return send_file(f'/home/oskar/project/downloaded/{path_name}.zip', as_attachment=True)
        
    
    else:
        #remove all the files in the downloaded directory to create space
        shutil.rmtree('/home/oskar/project/downloaded')
        os.makedirs('downloaded')
        return render_template('spotify_uri.html')

# progress bar dynamic update   
# @app.route('/progress')
# def progress(song):
#     def generate(x):
#             print(x, "lol")
#             yield "data:" + str(x) + "\n\n"
#     return Response(generate(song), mimetype= 'text/event-stream')

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
@app.route("/playlists", methods=["GET", "POST"])
def get_playlists():
    
    from func import api_json, get_song
    #if the login went wrong
    if 'access_token' not in session:
        return redirect('/login')
    #if session expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    #request function
    if request.method == 'GET':
        from func import api_json
        
        playlists = api_json('me/playlists?limit=6')
        #get all the items I need fro the playlists
        
        #different variables which I'm going to use
        images_url = []
        name = []
        tracks_href = [] 
        tracks_total = []
        id = []
        playlist_range = playlists['total']
        
        #nested for loop to get the specific information
        for playlist in playlists['items']:
            for i in playlist['images']:
                if i['height'] == 300:
                    images_url.append(i['url'])
            
            tracks_total.append(playlist['tracks']['total'])
            tracks_href.append(playlist['tracks']['href'])
            name.append(playlist['name'])
            id.append(playlist['id'])
        
        # remove folders from other downloads
        shutil.rmtree('/home/oskar/project/downloaded')
        os.makedirs('downloaded')

        return render_template('index.html', images_url=images_url, name=name, tracks_href=tracks_href, tracks_total=tracks_total, playlist_range=playlist_range, id=id)
    else:
        #get the url
        url = request.form.get('url')
       
    
        #send the api request and get response
        playlist = api_json(f'playlists/{url}/tracks?limit=50')
        #name of the playlist
        pl_n = api_json(f'playlists/{url}')
        
        playlist_name = pl_n['name']
        
        tracks_total = playlist['total']
        name = []
        artist = []

        for i in playlist['items']:
            name.append(i['track']['name'])
            for b in i['track']['artists']:
                if b['name'] == "":
                    artist.append("null")
                else:
                    artist.append(b['name'])

        #create a path where to store the songs
        
        path_name = playlist_name
        path = f'/home/oskar/project/downloaded/{path_name}'
        os.mkdir(path)
        #counter of songs downloaded
        # counter = 0
        if tracks_total > 50:
            tracks_total == 50
        for i in range(tracks_total):
            get_song(name[i], path_name)
        
        shutil.make_archive(f'{path_name}', 'zip', f'/home/oskar/project/downloaded/{path_name}')
        
        shutil.move(f'{path_name}.zip', '/home/oskar/project/downloaded')
        
        return send_file(f'/home/oskar/project/downloaded/{path_name}.zip', as_attachment=True)


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
