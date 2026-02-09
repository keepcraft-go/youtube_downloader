# downloader/youtube.py
from yt_dlp import YoutubeDL

def download_video(url):
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        # 최고화질 mp4 비디오 + 최고음질 오디오 병합
        # 없으면 최고화질 mp4
        # 그것도 없으면 최고 품질
        
        "merge_output_format": "mp4",  # 병합 시 mp4로
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info)