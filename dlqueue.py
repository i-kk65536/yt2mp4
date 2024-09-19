import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
import re
import subprocess
from typing import Any, Callable
import threading

import flet as ft
from yt_dlp import YoutubeDL

class Queue(ft.UserControl):
    def __init__(self, download_format: dict):
        super().__init__()
        self.previous_download_rate = 0.
        self.text_status = ft.Text(
            value="DOWNLOADING",
            width=None,
        )
        self.progress_bar = ft.ProgressBar(
            value=0,
            expand=True,
        )
        self.startThread(self.downloadWithYoutubeDL, download_format)

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.text_status,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            self.progress_bar,
                        ],
                    ),
                ],
            ),
            margin=10,
            padding=30,
        )
    
    def startThread(self, target: Callable[..., None], *args: Any) -> None:
        self.thread = threading.Thread(target=target, args=args)
        self.thread.daemon = True
        self.thread.start()

    def downloadWithYoutubeDL(self, format: dict) -> None:
        url = format["url"]
        ydl_opts = {
            "format": "bestvideo+bestaudio",
            "outtmpl": format["path"] + "%(title)s.%(ext)s",
            "formatsort": ["br"],
            "merge_output_format": "mp4",
            "progress_hooks": [self.updateProgressBar]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        self.renameDate(format["path"], format["formatted_date"], format["title"], format["ext"])
        self.page.window_destroy()

    def updateProgressBar(self, progress: dict[str, str]) -> None:
        def isVideo(info: dict[str, str | list[dict]]) -> bool:
            current_format = info["format"]
            format_id = re.match(r'(\d+) -', current_format).group(1)
            format_list = info["formats"]
            for format in format_list:
                if format.get('format_id') == format_id:
                    if format.get('vcodec') != "none":
                        return True
            return False

        if progress["status"] == "downloading":
            if isVideo(progress['info_dict']):
                self.text_status.value = "VIDEO DOWNLOADING..."
            elif not isVideo(progress['info_dict']):
                self.text_status.value = "AUDIO DOWNLOADING..."
            download_rate = float(re.sub(r'\x1b\[[0-9;]*m', '', progress['_percent_str']).replace("%", "").strip()) / 100
            if self.previous_download_rate < download_rate or self.previous_download_rate - download_rate > 0.1:
                self.progress_bar.value = download_rate
                self.previous_download_rate = download_rate
        elif progress["status"] == "finished":
            if not isVideo(progress['info_dict']):
                self.text_status.value = "COMPLETED"
        self.update()
    
    def renameDate(self, path: str, date: str, title: str, ext: str) -> None:
        if not date:
            return
        old_path = f"{path}{title}.{ext}"
        new_path = f"{path}{date} {title}.{ext}"
        try:
            os.rename(old_path, new_path)
        except:
            window_title = "error"
            error_message = "FAILED TO RENAME"
            self.showDialog(window_title, error_message)

    def showDialog(self, title: str, message: str) -> None:
        command = ["python", "dialog.py", title, message]
        subprocess.Popen(command)

def runQueue(format: dict) -> None:
    def queue(page: ft.Page, format: dict) -> None:
        page.title = "queue"
        page.window_width = 384
        page.window_height = 288
        page.theme = ft.Theme(font_family="源ノ角ゴシック Code JP")
        page.window_always_on_top = True

        view = Queue(download_format=format)
        
        page.add(view)

    ft.app(target=lambda page: queue(page, format))

if __name__ == "__main__":
    def dict(json_data: str) -> dict:
        return json.loads(json_data)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("format", type=dict)
    args = parser.parse_args()

    runQueue(args.format)