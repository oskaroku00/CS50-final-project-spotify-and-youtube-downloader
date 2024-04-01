from pytubefix import YouTube
from pytubefix import Search
from pytubefix.exceptions import RegexMatchError, VideoUnavailable

search = Search('abc')
y = search.videos[0]

video = YouTube(f'https://www.youtube.com/watch?v={y}')
video = video.streams.get_audio_only()

video.download(output_path=f'downloaded/', mp3 = True , timeout=120, max_retries=1)

