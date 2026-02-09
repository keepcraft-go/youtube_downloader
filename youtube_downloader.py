#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 다운로더 - 비디오 및 오디오 추출 도구
사용자 친화적인 GUI 기반 다운로더
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
import yt_dlp


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 다운로더")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # 다운로드 경로 기본값
        self.download_path = str(Path.home() / "Downloads")
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 타이틀
        title_label = ttk.Label(
            main_frame, 
            text="🎬 YouTube 다운로더",
            font=("맑은 고딕", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL 입력
        url_label = ttk.Label(main_frame, text="YouTube URL:", font=("맑은 고딕", 10))
        url_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.url_entry = ttk.Entry(main_frame, width=60, font=("맑은 고딕", 10))
        self.url_entry.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 다운로드 타입 선택
        type_label = ttk.Label(main_frame, text="다운로드 타입:", font=("맑은 고딕", 10))
        type_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.download_type = tk.StringVar(value="both")
        
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        ttk.Radiobutton(
            type_frame, 
            text="비디오 + 오디오", 
            variable=self.download_type, 
            value="both"
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            type_frame, 
            text="비디오만", 
            variable=self.download_type, 
            value="video"
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            type_frame, 
            text="오디오만 (MP3)", 
            variable=self.download_type, 
            value="audio"
        ).pack(side=tk.LEFT)
        
        # 저장 경로
        path_label = ttk.Label(main_frame, text="저장 경로:", font=("맑은 고딕", 10))
        path_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.path_entry = ttk.Entry(path_frame, width=50, font=("맑은 고딕", 9))
        self.path_entry.insert(0, self.download_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        path_button = ttk.Button(path_frame, text="찾아보기", command=self.browse_folder)
        path_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 진행 상태
        self.progress_label = ttk.Label(
            main_frame, 
            text="다운로드 대기 중...",
            font=("맑은 고딕", 9)
        )
        self.progress_label.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=650
        )
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 다운로드 버튼
        self.download_button = ttk.Button(
            main_frame,
            text="다운로드 시작",
            command=self.start_download,
            style="Accent.TButton"
        )
        self.download_button.grid(row=9, column=0, columnspan=3, pady=10)
        
        # 로그 영역
        log_label = ttk.Label(main_frame, text="다운로드 로그:", font=("맑은 고딕", 9))
        log_label.grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = tk.Text(main_frame, height=8, width=80, font=("맑은 고딕", 9))
        self.log_text.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=11, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def browse_folder(self):
        """폴더 선택 다이얼로그"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def progress_hook(self, d):
        """다운로드 진행 상태 업데이트"""
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                self.progress_label.config(
                    text=f"다운로드 중: {percent} | 속도: {speed} | 남은 시간: {eta}"
                )
            except:
                self.progress_label.config(text="다운로드 중...")
        elif d['status'] == 'finished':
            self.progress_label.config(text="다운로드 완료! 파일 변환 중...")
            
    def download_video(self, url, download_type):
        """실제 다운로드 수행"""
        try:
            self.log(f"URL: {url}")
            self.log(f"타입: {download_type}")
            self.log(f"저장 경로: {self.download_path}")
            self.log("-" * 60)
            
            # yt-dlp 옵션 설정
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            }
            
            if download_type == "audio":
                # 오디오만 다운로드 (MP3)
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
                self.log("오디오(MP3) 다운로드를 시작합니다...")
                
            elif download_type == "video":
                # 비디오만 다운로드
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                self.log("비디오 다운로드를 시작합니다...")
                
            else:  # both
                # 비디오 + 오디오 별도 다운로드
                self.log("비디오와 오디오를 모두 다운로드합니다...")
                
                # 1. 비디오 다운로드
                video_opts = ydl_opts.copy()
                video_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                
                self.log("\n[1/2] 비디오 파일 다운로드 중...")
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_title = info.get('title', 'video')
                    self.log(f"✓ 비디오 다운로드 완료: {video_title}")
                
                # 2. 오디오 다운로드
                audio_opts = ydl_opts.copy()
                audio_opts.update({
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.download_path, '%(title)s_audio.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
                
                self.log("\n[2/2] 오디오 파일(MP3) 다운로드 중...")
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    ydl.download([url])
                    self.log(f"✓ 오디오 다운로드 완료: {video_title}_audio.mp3")
                
                self.progress_label.config(text="모든 다운로드 완료!")
                self.log("\n" + "=" * 60)
                self.log("✓ 다운로드가 모두 완료되었습니다!")
                self.log(f"저장 위치: {self.download_path}")
                messagebox.showinfo("완료", "다운로드가 완료되었습니다!")
                return
            
            # audio 또는 video 단일 다운로드
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')
                
                self.progress_label.config(text="다운로드 완료!")
                self.log("\n" + "=" * 60)
                self.log(f"✓ 다운로드 완료: {title}")
                self.log(f"저장 위치: {self.download_path}")
                messagebox.showinfo("완료", "다운로드가 완료되었습니다!")
                
        except Exception as e:
            error_msg = f"오류 발생: {str(e)}"
            self.log(f"\n❌ {error_msg}")
            self.progress_label.config(text="다운로드 실패")
            messagebox.showerror("오류", error_msg)
            
        finally:
            self.progress_bar.stop()
            self.download_button.config(state="normal")
            
    def start_download(self):
        """다운로드 시작"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력해주세요!")
            return
            
        if not url.startswith(('http://', 'https://')):
            messagebox.showwarning("경고", "올바른 URL을 입력해주세요!")
            return
        
        # UI 상태 변경
        self.download_button.config(state="disabled")
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        
        # 별도 스레드에서 다운로드 실행
        download_type = self.download_type.get()
        thread = threading.Thread(
            target=self.download_video,
            args=(url, download_type),
            daemon=True
        )
        thread.start()


def main():
    """메인 함수"""
    root = tk.Tk()
    
    # 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')
    
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
