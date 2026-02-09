# downloader/youtube.py
from yt_dlp import YoutubeDL

def download_video(url):
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "format": "best"
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info)
