import requests
import json
import re
#youtube api to search and download the music
from pytubefix import YouTube
from pytubefix import Search
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
from main import session, API_BASE_URL

#get the JSON from spotify using the url and optional arguments
def api_json(url):
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + url, headers=headers).json()
    response = json.loads(json.dumps(response))

    return response

#get and download the music from spotify
def get_song(name, artist, path):

    if artist == "null":
        search = Search(f'{name} - song')
    else:
        search = Search(f'{name} - {artist}')
    
    yt = search.results[0]

    ys = yt.streams.get_audio_only()
    ys.download(output_path=f'downloaded/{path}', mp3=True , timeout=120, max_retries=1)
# filename=f'{name}.mp3'
#get and download the music from the url
def get_song_url(url):
    try:
        yt = YouTube(url)

    except RegexMatchError: 
        return 1
    else:
        ys = yt.streams.get_audio_only()
        try: 
            ys.download(output_path='downloaded', mp3=True, timeout=120, max_retries=1)
        except VideoUnavailable:
            return 2
        return yt.title


