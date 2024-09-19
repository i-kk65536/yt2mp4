from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import json
import re
import subprocess
import threading
from typing import Any, Callable, Tuple
import urllib.parse

import flet as ft
import pyperclip
from yt_dlp import YoutubeDL

# PULLREQUEST
# settings.jsonファイルから取得できるようにする
DOWNLOAD_PATH = "D:\\Users\\LOCKE256\\Videos\\youtube\\"

class Body(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.is_downloaded = {}
        self.thread = None
        self.image_thumbnail = ft.Image(
            src="./source/dummy.png",
            width=256,
        )
        self.input_url = ft.TextField(
            label="URL",
            on_change=self.input_url_changed,
            expand=True,
        )
        self.option_quality = ft.Dropdown(
            label="QUALITY",
            on_change=self.option_quality_selected,
            expand=True,
        )
        self.button_download = ft.ElevatedButton(
            text="DOWNLOAD",
            icon=ft.icons.DOWNLOAD,
            on_click=self.download_clicked,
            width=None,
        )
        self.text_output = ft.Text(
            value="OUTPUT",
            width=None,
            visible=False,
        )
        self.text_title = ft.Text(
            value="",
            width=None,        
        )
        self.option_extension = ft.Dropdown(
            label="EXTENSION",
            width=150,
            visible=False,
        )
        self.text_quality = ft.Text(
            value="QUALITY:",
            width=None,
            visible=False,
        )
        self.text_video_quality = ft.Text(
            value="",
            width=None,
        )
        self.text_audio_quality = ft.Text(
            value="",
            width=None,
        )
        self.checkbox_video = ft.Checkbox(
            label="VIDEO",
            value=True,
            width=None,
            visible=False,
        )
        self.checkbox_audio = ft.Checkbox(
            label="AUDIO",
            value=True,
            width=None,
            visible=False,
        )
        self.checkbox_playlist = ft.Checkbox(
            label="PLAYLIST",
            value=False,
            width=None,
            visible=False,
        )
        self.checkbox_thumbnail = ft.Checkbox(
            label="THUMBNAIL",
            value=False,
            width=None,
            visible=False,
        )
        self.checkbox_comment = ft.Checkbox(
            label="COMMENT",
            value=False,
            width=None,
            visible=False,
        )
        self.checkbox_chat = ft.Checkbox(
            label="CHAT (LIVE ONLY)",
            value=False,
            width=None,
            visible=False,
        )
        self.startThread(self.setInputURL)

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.image_thumbnail,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            self.input_url,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            self.option_quality,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            self.button_download,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            self.text_output,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            self.text_title,
                            self.option_extension,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self.text_quality,
                                    ],
                                ),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self.text_video_quality,
                                        self.text_audio_quality,
                                    ],
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self.checkbox_video,
                                        self.checkbox_playlist,
                                        self.checkbox_comment,
                                    ],
                                ),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self.checkbox_audio,
                                        self.checkbox_thumbnail,
                                        self.checkbox_chat,
                                    ],
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
            ),
            margin=10,
            padding=30,
        )

    def input_url_changed(self, event: ft.ControlEvent) -> None:
        self.thread.join()
        self.startThread(self.onChangeInputURL)

    def download_clicked(self, event: ft.ControlEvent) -> None:
        def isDownloaded() -> bool:
            if self.is_downloaded.get(self.info_dict["title"], False):
                return True
            else:
                self.is_downloaded[self.info_dict["title"]] = True
                return False
            
        self.thread.join()
        if isDownloaded():
            return
        format_dict = self.createDownloadFormat()
        format_json = json.dumps(format_dict)
        command = ["python", "dlqueue.py", format_json]
        subprocess.Popen(command)

    def option_quality_selected(self, event: ft.ControlEvent) -> None:
        self.thread.join()
        self.startThread(self.onSelectOptionQuality)
    
    def startThread(self, target: Callable[..., None], *args: Any) -> None:
        self.thread = threading.Thread(target=target, args=args)
        self.thread.daemon = True
        self.thread.start()
        
    def setInputURL(self) -> None:
        self.input_url.value = self.waitForInput()
        self.onChangeInputURL()

    def onChangeInputURL(self) -> None:
        self.update()
        try:
            self.info_dict = self.fetchVideoInfo()
        except:
            self.option_quality.options = []
            self.text_output.visible = False
            self.text_title.visible = False
            self.option_extension.visible = False
            self.text_quality.visible = False
            self.text_video_quality.visible = False
            self.text_audio_quality.visible = False

            self.update()
            return
        self.setThumbnail()
        self.setOptionQuality()
        self.setTextOutput()
        self.setTextTitle()
        self.setOptionExtension()
        self.setTextQuality()
        self.update()

    def onSelectOptionQuality(self) -> None:
        self.setTextQuality()
        self.update()

    def createDownloadFormat(self) -> dict[str, str | bool]:
        format = {
            "url": self.input_url.value,
            "path": DOWNLOAD_PATH,
            "formatted_date": self.upload_date,
            "title": self.info_dict["title"],
            "ext": self.option_extension.value,
        }
        return format

    def waitForInput(self) -> str:
        def isURL(text: str) -> bool:
            search_string_list = ["youtube.com", "youtu.be"]
            return any(search_string in text for search_string in search_string_list)
        
        while not isURL(clipboard_content := pyperclip.waitForPaste()):
            pyperclip.copy("")
        return clipboard_content

    def fetchVideoInfo(self) -> dict:
        def convertURL(url: str) -> str:
            pattern = ['https://www.youtube.com/watch?', 'https://youtu.be/']
            if re.match(pattern[0], url):
                url_query = urllib.parse.urlparse(url).query
                video_query = urllib.parse.parse_qs(url_query)['v'][0]
                formatted_url = f"https://www.youtube.com/watch?v={video_query}"
                if playlist_query := urllib.parse.parse_qs(url_query).get("list", False) and self.checkbox_playlist.value:
                    formatted_url += f"&list={playlist_query[0]}"
                    if index_query := urllib.parse.parse_qs(url_query).get("index", False):
                        formatted_url += f"&index={index_query[0]}"
            elif re.match(pattern[1], url):
                formatted_url = f"https://www.youtube.com/watch?v={url[17:28]}"
                if "list" in url[28:] and self.checkbox_playlist.value:
                    formatted_url += f"&list={url[34:]}"
            return formatted_url
        
        url = convertURL(self.input_url.value)
        ytdlp_options = {
            "listformats": True
        }
        with YoutubeDL(ytdlp_options) as ydl:
            info_dict = ydl.extract_info(url, download=False)
        return info_dict

    def setThumbnail(self) -> None:
        self.image_thumbnail.src = self.lookupThumbnailURL()

    def setOptionQuality(self) -> None:
        self.option_quality.options = self.buildOptionQuality()
        self.option_quality.key = self.option_quality.options[0].key
        self.option_quality.value = self.option_quality.options[0].key

    def setTextOutput(self) -> None:
        self.text_output.visible = True
       
    def setTextTitle(self) -> None:
        self.text_title.value = self.lookupTextTitle()
        self.text_title.visible = True

    def setOptionExtension(self) -> None:
        self.option_extension.options = self.buildOptionExtension()
        self.option_extension.value = self.option_extension.options[0].key
        self.option_extension.visible = True

    def setTextQuality(self) -> None:
        self.text_video_quality.value, self.text_audio_quality.value = self.buildTextQuality()
        self.text_quality.visible = True
        self.text_video_quality.visible = True
        self.text_audio_quality.visible = True

    def lookupThumbnailURL(self) -> str:
        return self.info_dict.get("thumbnail", "")

    def buildOptionQuality(self) -> list[ft.dropdown.Option]:
        def lookupVideoQuality(info_dict: dict) -> dict[str, dict[str, str]]:
            def calcResolution(res: str) -> int:
                if "x" in res:
                    width, height = res.split("x")
                    return int(width) * int(height)
                return 0
            
            format_list: list[dict] = info_dict.get("formats", [])
            video_format_list = [format for format in format_list if format.get("vcodec") != "none"]
            quality_dict = {}
            for format in video_format_list:
                format_id = format.get("format_id")
                ext = format.get("ext")
                resolution = format.get("resolution") or f"{format.get('width', '')}x{format.get('height', '')}"
                fps = format.get("fps")
                vcodec = format.get("vcodec")
                vbr = str(format.get("vbr", "")) + "k"
                filesize = (str(round(format.get("filesize", 0) / 1024**2, 1)) + "MiB") if format.get("filesize") else "Unknown"
                option = {
                    "format_id" : str(format_id),
                    "ext"       : str(ext),
                    "resolution": str(resolution),
                    "fps"       : str(fps),
                    "vcodec"    : str(vcodec),
                    "vbr"       : str(vbr),
                    "filesize"  : str(filesize)
                }
                quality_dict[format_id] = option
            quality_dict = dict(sorted(quality_dict.items(), key=lambda item: calcResolution(item[1]["resolution"]), reverse=True))
            return quality_dict
        
        self.video_quality_dict = lookupVideoQuality(self.info_dict)
        for_option_key_list = ["ext", "resolution", "fps", "vcodec", "vbr", "filesize"]
        max_width = {key: max(len(option[key]) for option in self.video_quality_dict.values()) for key in for_option_key_list}

        option_video_quality_list = []
        for format_id, option in self.video_quality_dict.items():
            option_text = (
                f"{option['ext'].ljust(max_width['ext'])}  "
                f"{option['resolution'].ljust(max_width['resolution'])}  "
                f"{option['fps'].ljust(max_width['fps'])}  "
                f"{option['vcodec'].ljust(max_width['vcodec'])}  "
                f"{option['vbr'].ljust(max_width['vbr'])}  "
                f"{option['filesize'].ljust(max_width['filesize'])}"
            )
            option_video_quality_list.append(ft.dropdown.Option(key=format_id, text=option_text))

        return option_video_quality_list

    def lookupTextTitle(self) -> str:
        def convertDateFormat(date: str, format: str) -> str:
            try:
                if not format:
                    return ""
                date_obj = datetime.strptime(date, "%Y%m%d")
                format = format.replace('yyyy', '%Y').replace('yy', '%y').replace('MM', '%m').replace('dd', '%d')
                if any(char in format for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']):
                    raise ValueError('Invalid format: contains invalid characters')
                formatted_date = date_obj.strftime(format)
            except (ValueError, KeyError):
                formatted_date = date
            return formatted_date

        title = self.info_dict.get("title", "")
        raw_upload_date = self.info_dict.get("upload_date", "")
        # PULLREQUEST
        # filename_formatは将来的にsetting.jsonから取得する予定
        filename_format = "yyyy-MM-dd"
        self.upload_date = convertDateFormat(raw_upload_date, filename_format)
        return f"{self.upload_date} - {title}" if self.upload_date else title

    def buildOptionExtension(self) -> list[ft.dropdown.Option]:
        extension_list = ["mp4", "mkv", "mov", "webm"]
        return [ft.dropdown.Option(key=extention, text=extention) for extention in extension_list]
    
    def buildTextQuality(self) -> Tuple[str, str]:
        def lookupAudioQuality(info_dict: dict) -> dict[str, dict[str, str]]:
            def perseAbr(abr: str) -> float:
                if abr == "Unknown":
                    return 0
                return float(abr[:abr.find("k")])
            def calcAcodecPriority(acodec: str) -> int:
                # PULLREQUEST
                # 優先順位をsetteng.jsonから取得できるように
                priorities = {
                    "opus": 7,
                    "vorbis": 6,
                    "aac": 5,
                    "mp4a": 4,
                    "mp3": 3,
                    "ac3": 2,
                    "dts": 1
                }
                return priorities.get(acodec, 0)
                
            format_list: list[dict] = info_dict.get("formats", [])
            audio_format_list = [format for format in format_list if format.get("acodec") != "none"]
            quality_dict = {}
            for format in audio_format_list:
                format_id = format.get("format_id")
                ext = format.get("ext")
                samplerate = format.get("samplerate")
                acodec = format.get("acodec")
                abr = str(format.get("abr", "")) + "k" if format.get("abr", "") else "Unknown"
                filesize = (str(round(format.get("filesize", 0) / 1024**2, 1)) + "MiB") if format.get("filesize") else "Unknown"
                option = {
                    "format_id" : str(format_id),
                    "ext"       : str(ext),
                    "samplerate": str(samplerate),
                    "acodec"    : str(acodec),
                    "abr"       : str(abr),
                    "filesize"  : str(filesize)
                }
                quality_dict[format_id] = option
            quality_dict = dict(sorted(quality_dict.items(), key=lambda item: (perseAbr(item[1]["abr"]), calcAcodecPriority(item[1]["acodec"])), reverse=True))
            return quality_dict
        
        video_format_id = self.option_quality.value
        current_video_quality_dict = {
            "ext"       : self.video_quality_dict[video_format_id]["ext"],
            "vcodec"    : self.video_quality_dict[video_format_id]["vcodec"],
            "resolution": self.video_quality_dict[video_format_id]["resolution"],
            "fps"       : f"{self.video_quality_dict[video_format_id]['fps']}fps" if (self.video_quality_dict[video_format_id].get("fps") != "None") else "",
            "vbr"       : f"{self.video_quality_dict[video_format_id]['vbr']}bps" if (self.video_quality_dict[video_format_id].get("vbr") != "None") else "",
        }
        self.audio_quality_dict = lookupAudioQuality(self.info_dict)
        audio_format_id = next(iter(self.audio_quality_dict))
        current_audio_quality_dict = {
            "ext"       : self.audio_quality_dict[audio_format_id]["ext"],
            "acodec"    : self.audio_quality_dict[audio_format_id]["acodec"],
            "samplerate": f"{self.audio_quality_dict[audio_format_id]['samplerate']}Hz" if (self.audio_quality_dict[audio_format_id].get("samplerate") != "None") else "",
            "abr"       : f"{self.audio_quality_dict[audio_format_id]['abr']}bps" if (self.audio_quality_dict[audio_format_id].get("abr") != "None") else "",
        }
        max_width = [
            max(
                len(current_video_quality_dict["ext"]),
                len(current_audio_quality_dict["ext"])
            ),
            max(
                len(current_video_quality_dict["vcodec"]),
                len(current_audio_quality_dict["acodec"])
            ),
            max(
                # resolutionのあとの空白1文字
                (resolution_length := len(current_video_quality_dict["resolution"]) + 1) + (fps_length := len(current_video_quality_dict["fps"])),
                len(current_audio_quality_dict["samplerate"])
            ),
            max(
                len(current_video_quality_dict["vbr"]),
                len(current_audio_quality_dict["abr"])
            )
        ]

        text_video_quality = (
            f"{current_video_quality_dict['ext'].ljust(max_width[0])} " + 
            f"{current_video_quality_dict['vcodec'].ljust(max_width[1])} " + 
            f"{current_video_quality_dict['resolution']} " + 
           (f"{current_video_quality_dict['fps']} "  if (max_width[2] == resolution_length + fps_length) else (f"{current_video_quality_dict['fps'].ljust(max_width[2] - resolution_length)} ")) + 
            f"{current_video_quality_dict['vbr'].ljust(max_width[3])} "
        )

        text_audio_quality = (
            f"{current_audio_quality_dict['ext'].ljust(max_width[0])} "
            f"{current_audio_quality_dict['acodec'].ljust(max_width[1])} "
            f"{current_audio_quality_dict['samplerate'].ljust(max_width[2])} "
            f"{current_audio_quality_dict['abr'].ljust(max_width[3])} "
        )

        return text_video_quality, text_audio_quality
