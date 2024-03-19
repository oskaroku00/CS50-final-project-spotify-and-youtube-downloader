
from pytubefix import YouTube
from pytubefix import Search
from pytubefix.exceptions import RegexMatchError
yt = YouTube('https://www.youtube.com/watch?v=vQBI9y_bAjU&ab_channel=TheElectricSwingCircus-Topic')
t = yt.streams.get_audio_only()
t.download(mp3=True)
