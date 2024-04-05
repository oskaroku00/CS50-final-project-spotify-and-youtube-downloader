# SIMPLE SPOTIFY AND YOUTUBE DOWNLOADER

#### Video Demo:  <URL HERE>

#### Description of the project: 

As the name suggests, is a spotify an youtube downloader using the videos URL and the information from the users Spotify accounts.

Saves the individual videos in **.mp3** format.

Playlists are saved in the **.zip** format and the songs in the same **.mp3**.

Any user data is stored.

------------

####  Features :

- YouTube single download video
- Spotify Token api login
- Spotify API info grabbing 
- User playlist information
- User Playlist downloads 
- URL playlist download

------------

#### Dependences :

- **Flask framework**
- [Bootstrap](http://getbootstrap.com/ "Bootstrap")  **(css)** / [Templated](http:templated.co/ "Templated") **(html , some css)**

- ##### Python dependences :
	 - **pytubefix** (searching and wideo downloading function)
     - **requests** (making requests to the api)
	 - **json** (respopnses from the api)
	 - **base64** (encryption)
	 - **urllib** (parsing strings)
	 - **os** (folder and file management)
	 - **datetime** (token expiration management)
	 - **shutil** (zip file compression, removing files)

------------

#### How to use :
If you wan to download this project and use it you will need to sign up into the Spotify Web API and create your own dashboard where you are going to find the **CLIENT_ID** and the **CLIENT_SECRET** which you will need to change before in **main.py**

###### lines main.py

>  **21 22 23**

    CLIENT_ID = '*********************************'
    CLIENT_SECRET = '*****************************'
    REDIRECT_URI = 'http://127.0.0.1:5000/callback' 

> The redirect_uri is changed in the developer dashboard (redirect url)

Additionally you also will need to change some **folder** **paths** which are complete and not relative

###### lines main.py

> **56 117 133 135 137 142 254 285 294 296 298**

------------

#### Design :

###### templates folder (html files) :

- index.html (homepage and last listened playlist download) 
- youtube.html (youtube- URL download single video download)
- spotify_url.html (URL playlist download)

###### python files :

- main.py (all server information is stored)
-  func.py (some usefull functions I wrote because I use them repeatedly)

###### other folders :

- The static folder is where the css and the fonts are saved
- The download folder is where the songs and playlist are temporarily stored , sended and deleted

#### Functions :

- #### api_json(url) :

	Makes use of the spotify api creating a request of any kind when provided whith a **valid URL endpoint** and returns a python dict of the response

	```python
	def api_json( url ) :
		#creating header of the request
		headers = {
			'Authorization': f"Bearer {session['access_token']}"
		}
		#sending the request
		response = requests.get(API_BASE_URL + url, headers=headers).json()
		#transforming the request into a python dict
		response = json.loads(json.dumps(response))

		return response
	```

- #### get_song( name, path ) :

	 Downloads a single song from youtube giveing the **name** as argument and the **path** where it will be stored
	 
	 It is used to download entier Playlists

	 ```python
	#get and download the music from spotify
	def get_song(name, path):
		#searching of the song
		
		search = Search(f'{name} - song')
		
		#downloading the song
		yt = search.results[0]
		ys = yt.streams.get_audio_only()
		ys.download(output_path=f'downloaded/{path}', mp3=True , timeout=120, max_retries=1)
	```

- #### get_song_url( url ) :

	Downloads a single song from youtube giveing the **URL** of the video as argument
	
	It is used in the youtube URL downloader

	```python
	#get and download the music from the url
	def get_song_url(url):
		#checking if the url is valid
		try:
			yt = YouTube(url)

		except RegexMatchError: 
			return 1
		else:
			#try if the download is possible
			try: 
				ys = yt.streams.get_audio_only()
				ys.download(output_path='downloaded', mp3=True, timeout=120, max_retries=1)
			except VideoUnavailable:
				return 2
			#returning the title for the file name
			return yt.title
	```

#### How it works :


- #### /youtube 
	
	When you enter the root page you will be greeted with the youtube.html because you dont need to log in to use it. 
	
	Is designed to be simple enough for everyone.

	The user is going to find a form where they are going to paste a URL and a button to download a single video
	
	It haves some safety for the **user imput** :

	```python
	if video == 1:
		flash('Invalid URL')
		return render_template('youtube.html') 
	if video == 2:
		flash("Couldn't download, or invalid URL")
		return render_template('youtube.html')
	```

	Makes use of the **get_song_url( url )** function  

- #### /login

	The user is redirected to login if he wants to access to the **Spotify** functionality
	
	It creates a request with a scope and some parameters which redirect the user to the **spotify login page**

- #### /callback

	Where the spotify api sends all the information we need to create an **access token**

	Heare we send an **API request** which returns the valid **Token** for the user

	```python
	# token important data
	session['access_token'] = token_info['access_token']
	session['refresh_token'] = token_info['refresh_token']
	# when the token expires
	session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
	```

	> the token lasts 3600s or 1h

- #### /refresh_token

	If the **Token** has expired we send the user to the refresh_token page where is automatically refreshed

- #### /playlists

	> The **get** method

	With the **access token**  it calls the **api_json( url )** function to get the 6 last listened playlist in their account, and displays the playlist in a table next to other information about the playlist and the download button

	```python
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
	```

	> The **post** method

	When the user clicks the download button the download process begins calling the **api_json( url )** function and getting all 	the relevant information about the playlist 

	```python
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
	```

	- 	Then it creates a new folder to store all the songs
	- 	Downloads all the songs using the **get_song( name, path )** function
	- 	Stores all the songs in the created folder
	- 	Makes a .zip
	- 	Sends the .zip to the user 

- #### /spotify_uri 

	The user is going to find a form where they are going to paste a **URL** and a **button** to download a single playlist
	It haves some safety for the **user imput** :
	
	```python
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
	```

	When the user clicks the download button the page does the same process of **/playlists**


------------


#### Design flaws :
The page has some design flaws, like the maximum amount of 50 songs you can download at once or when sometimes wrong songs are downloaded

At first I wanted to code a progress bar for the playlist downloader because of the long wait times, using an event listener and some server code which would return a value for the bootstrap progress bar :

> client side code

```javascript
var source = new EventSource("/progress");
	source.onmessage = function(event) {
		$('.progress-bar').css('width', event.data+'%').attr('aria-valuenow', event.data);   
	}
```
```html
<div class="progress" style="width: 100%;">
	<div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>
</div>
```

> server side code


```python
@app.route('/progress')
def progress(song):
    def generate(x):
            return "data:" + str(x) + "\n\n"
    return Response(generate(song), mimetype= 'text/event-stream')
```
> I couldnt make that the user recived any data from the server that which could affect the page

------------
