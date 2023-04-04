# ############################################################# 
# BiliMusic Main                                                 
# Copyright (C) 2023 cmderli. This program is a free software.
# #############################################################
VERSION = 'bilimusic v0.1'
COPYRIGHT = """

版权所有 (C) 2023 程序猿李某人(cmderli)
本软件是自由软件；你可以按照由自由软件基金会发布的GNU通用公共许可证来再发布该软件或者修改该软件；
你可以使用该许可证的第3版，或者（作为可选项）使用该许可证的任何更新版本。
本程序的发布是希望它能发挥作用，但是并无担保；
甚至也不担保其可销售性或适用于某个特殊的目的。请参看GNU通用公共许可证来了解详情。
该程序应该同时附有一份GNU通用公共许可证的拷贝；如果没有，请参看<https://www.gnu.org/licenses>。

"""
import time
import asyncio
from bilibili_api import video, Credential, HEADERS, user, audio, sync, login
import httpx
import os
import requests
from PIL import Image
import flet as ft
import cover
import json
import threading
import mutagen
import mutagen.flac
import mutagen.mp3
import mutagen.id3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
import traceback
import hashlib
import pathlib
import bilimusic_i18n
import bilimusic_data
ILLEGAL_DIR_CHAR = ['<', '|', '>', '\\', '/', ':', '"', '*', '?'] # There is The Illegal Directory Characters.
SUPPORT_AUDIO_FORMAT = ('mp3', 'flac')
CWD = os.getcwd()
MAGIC_STRING = '6L+Z6YeM5LuA5LmI5Lmf5rKh5pyJ'
NOFACE = 'https://static.hdslb.com/images/member/noface.gif' # Thanks New Bing. https://sl.bing.net/cPB8OpQ9evc
badSettingFile = False
setting = {
    "language": "zh_CN",
    "SESSDATA": "",
    "BILI_JCT": "",
    "BUVID3": "",
    "DEDEUSERID": "",
    "theme_mode": False,
    "DOWNLOAD_DIR": CWD,
    "CACHE_DIR": CWD+"/.bilimusic_cache",
    "cacheAutoDelete": True,
    "FFMPEG": "ffmpeg",
    "decodeCommand": "{decoder} -i {input} -y -acodec {decodelib} {bitrate} {output}",
    "mp3Decoder": "libmp3lame -b:a",
    "flacDecoder": "flac -compression_level",
    "downloadEngine": "<Built-in>",
    "downloadEngineCommand": "{downloadEngine} {url} {output}",
    "ARTIST_DIVISION_CHAR": "/",
    "COVER_RES": 1024,
    "UA": "Mozilla/5.0",
    "FONT": "",
    "DOWNLOAD_CHUNK_SIZE": 1024,
    "DEFAULT_AUDIO_FORMAT": "mp3",
    "DEFAULT_AUDIO_BITRATE": "320k",
    "darkMode": False
}
def writeSettings(setting):
    with open('bilimusic.SETTINGS', 'w+', encoding='utf-8') as f:
        jsonString = json.dumps(setting)
        settingHash = hashlib.sha256(jsonString.encode('utf-8')).hexdigest()
        settingString = f'{MAGIC_STRING}\n{settingHash}\n{jsonString}'
        f.write(settingString)
def readSettings():
    with open('bilimusic.SETTINGS', 'r', encoding='utf-8') as f:
        jsonString = f.read()
        jsonStringList = jsonString.split('\n', 2)
        if len(jsonStringList) != 3:
            badSettingFile = True
            print('ERROR: BAD SETTING FILE.')
            return setting
        if jsonStringList[0] == MAGIC_STRING:
            settingHash = hashlib.sha256(jsonStringList[2].encode('utf-8')).hexdigest()
            if settingHash != jsonStringList[1]:
                badSettingFile = True
                print('ERROR: BAD SETTING FILE.')
                return setting
            else:
                settings = json.loads(jsonStringList[2])
                return settings
        # print(jsonStringList)
        #setting = json.loads(jsonString)
if not(os.path.exists('bilimusic.SETTINGS')):
    if not(os.path.exists(setting['CACHE_DIR'])):
        os.mkdir(setting['CACHE_DIR'])
    writeSettings(setting)
setting = readSettings()
languages = list()
lang_dict_unreversed = bilimusic_i18n.getI18nListDict()
lang_dict = dict()
for lang_name in lang_dict_unreversed:
    lang_dict[lang_dict_unreversed[lang_name]] = lang_name
    languages.append(lang_dict_unreversed[lang_name])
i18n = bilimusic_i18n.getI18nDict()
credential = Credential(setting["SESSDATA"], setting["BILI_JCT"], setting["BUVID3"], setting["DEDEUSERID"])
def biliGetMyInfo() -> dict:
    if credential.bili_jct != '':
        myBiliUser = user.User(uid=int(credential.dedeuserid),credential=credential)
        myInfo = sync(myBiliUser.get_user_info())
        with open(f'{setting["CACHE_DIR"]}/bilimusic.bilibili.user.info.{credential.dedeuserid}.json', 'w+') as infoFile:
            infoJsonString = json.dumps(myInfo)
            infoFile.write(infoJsonString)
        header = {"User-Agent": setting['UA']}
        coverpic = requests.get(myInfo["face"], headers=header) # Download Cover Image.
        with open(f'{setting["CACHE_DIR"]}/bilimusic.bilibili.user.face.{credential.dedeuserid}', 'wb+') as file: # Write Cover Image to cache.
            file.write(coverpic.content)
        # print(
        #     myBiliUser.get_uid(),
        #     myInfo
        # )
        return myInfo
    else:
        return {"face": NOFACE, "name": i18n["unLogin"]}

def biliQRLogin():
    credential = login.login_with_qrcode()
    print(
        credential.sessdata,
        credential.bili_jct,
        credential.has_bili_jct(),
        credential.buvid3,
        credential.dedeuserid,
        sep=",\n"
    )
    setting["SESSDATA"] = credential.sessdata
    setting["BILI_JCT"] = credential.bili_jct
    setting["BUVID3"] = credential.buvid3
    setting["DEDEUSERID"] = credential.dedeuserid
    writeSettings(setting)
if not(os.path.exists(setting['CACHE_DIR'])):
    setting['CACHE_DIR'] = CWD+'/.bilimusic_cache'
    with open('bilimusic.SETTINGS', 'w+', encoding='utf-8') as f:
        jsonString = json.dumps(setting)
        f.write(jsonString)
readLICENSE_GPLV3 = bilimusic_data.getData('LICENSE', 'str')
if readLICENSE_GPLV3 != None: # Load GPL v3.
    # open('LICENSE', 'r', encoding='utf-8').read()
    if readLICENSE_GPLV3 == '':
        LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
    else:
        LICENSE_GPLV3 = readLICENSE_GPLV3
else:
    if not(os.path.exists(f'{setting["CACHE_DIR"]}/bilimusic.license.gplv3.cache')):
        try:
            header = {"User-Agent": setting['UA']}
            gplv3 = requests.get('https://www.gnu.org/licenses/gpl-3.0.txt', headers=header) # https://www.gnu.org/licenses/gpl-3.0.txt
            LICENSE_GPLV3 = gplv3.content
            with open(f'{setting["CACHE_DIR"]}/bilimusic.license.gplv3.cache', 'w+', encoding='utf-8') as licenseCacheFile:
                licenseCacheFile.write(LICENSE_GPLV3.decode('utf-8'))
        except:
            # print(Error)
            LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
    else:
        readLICENSE_GPLV3 = open(f'{setting["CACHE_DIR"]}/bilimusic.license.gplv3.cache', 'r', encoding='utf-8').read()
        if readLICENSE_GPLV3 == '':
            LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
        else:
            LICENSE_GPLV3 = readLICENSE_GPLV3
class bilimusicApp:
    def __init__(self, page: ft.Page):
        # GUI Interface
        # I DON'T WANT TO WRITE COMMENTS.
        # 我不想写注释了...
        page.title = 'bilimusic'
        page.scroll = 'AUTO'
        if setting["darkMode"]:
            page.theme_mode = 'DARK'
            page.update()
        else:
            page.theme_mode = 'LIGHT'
            page.update()
        def closeMessage(dialog):
            dialog.open = False
            page.update()
        def showMessage(title, message):
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(message),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton(i18n["ok"], on_click=lambda _:closeMessage(dialog))
                ]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        # showMessage('Hello', 'World!')
        def showSnackBar(message):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(message)
            )
            page.snack_bar.open = True
            page.update()
        def advanceMkdir(path):
            try:
                Path = pathlib.Path(path)
                Path.mkdir(parents=True, exist_ok=True)
            except:
                Error = traceback.format_exc()
                showMessage(title = i18n["error"], message = f'{path} {Error}')
        def enableSettings(self):
            # Get settings in setup window and write settings.
            # global setting
            language = self.languageMenu.value
            language = lang_dict[language]
            cache_dir = self.cacheDirEntry.value
            download_dir = self.downloadDirEntry.value
            if cache_dir[-1::] == '\\' or cache_dir[-1::] == '/':
                cache_dir = cache_dir[:-1:]
            if download_dir[-1::] == '\\' or download_dir[-1::] == '/':
                download_dir = download_dir[:-1:]
            advanceMkdir(cache_dir)
            advanceMkdir(download_dir)
            if self.darkModeSwitch.value:
                page.theme_mode = 'DARK'
                page.update()
            else:
                page.theme_mode = 'LIGHT'
                page.update()
            try:
                i18n = bilimusic_i18n.getI18nDict()
                page.update()
            except:
                Error = traceback.format_exc()
                showMessage(title=i18n["error"], message=Error)
            setting = {
                "DOWNLOAD_DIR": download_dir,
                "CACHE_DIR": cache_dir,
                "language": language,
                "theme_mode": False,
                "cacheAutoDelete": self.cacheAutoDeleteButton.value,
                "FFMPEG": self.decoderBinEntry.value,
                "decodeCommand": self.decodeCommandEntry.value,
                "mp3Decoder": self.mp3DecoderEntry.value,
                "flacDecoder": self.flacDecoderEntry.value,
                "downloadEngine": self.downloadEngineEntry.value,
                "downloadEngineCommand": self.downloadEngineCommandEntry.value,
                "ARTIST_DIVISION_CHAR": self.artistDivisionCharEntry.value,
                "COVER_RES": int(self.coverResSlider.value),
                "UA": self.UAEntry.value,
                "FONT": "",
                "DOWNLOAD_CHUNK_SIZE": int(self.downloadChunkSizeSlider.value),
                "DEFAULT_AUDIO_FORMAT": self.defaultAudioFormatEntry.value,
                "DEFAULT_AUDIO_BITRATE": self.defaultAudioBitrateEntry.value,
                "darkMode": bool(self.darkModeSwitch.value),
                "SESSDATA": "",
                "BILI_JCT": "",
                "BUVID3": "",
                "DEDEUSERID": "",
            }
            writeSettings(setting)
            showMessage(i18n["finished"], i18n["writeSettingsFinished"])
        def settings(self):
            # self.languageEntry = ft.Dropdown()
            self.languageMenu = ft.Dropdown(label=i18n["language"],
                                     value=lang_dict_unreversed[setting["language"]],
                                     options=list(map(
                                        ft.dropdown.Option,
                                        languages
                                     )))
            self.darkModeSwitch = ft.Switch(label=i18n["darkMode"], value=setting["darkMode"])
            self.downloadDirEntry = ft.TextField(label=i18n["downloadDir"], 
                                                 value=setting["DOWNLOAD_DIR"])
            self.cacheDirEntry = ft.TextField(label=i18n["cacheDir"], 
                                              value=setting["CACHE_DIR"])
            self.cacheAutoDeleteButton = ft.Switch(label=i18n["cacheAutoDelete"], 
                                                   value=setting["cacheAutoDelete"])
            self.decoderBinEntry = ft.TextField(label=i18n["decoderBin"], 
                                                value=setting["FFMPEG"])
            self.decodeCommandEntry = ft.TextField(label=i18n["decodeCommand"], 
                                                   value=setting["decodeCommand"])
            self.mp3DecoderEntry = ft.TextField(label=i18n["mp3Decoder"], 
                                                value=setting["mp3Decoder"])
            self.flacDecoderEntry = ft.TextField(label=i18n["flacDecoder"], 
                                            value=setting["flacDecoder"])
            self.artistDivisionCharEntry = ft.TextField(label=i18n["artistDivisionChar"], 
                                                        value=setting["ARTIST_DIVISION_CHAR"])
            self.coverResText = ft.Text(i18n["coverRes"])
            self.coverResSlider = ft.Slider(min=64, 
                                            max=4096, 
                                            divisions=16, 
                                            label="{value}px", 
                                            value=setting["COVER_RES"])
            self.UAEntry = ft.TextField(label=i18n["UA"], 
                                            value=setting["UA"])
            self.downloadChunkSizeText = ft.Text(i18n["downloadChunkSize"])
            self.downloadChunkSizeSlider = ft.Slider(min=64, 
                                            max=4096, 
                                            divisions=16, 
                                            label="{value}", 
                                            value=setting["DOWNLOAD_CHUNK_SIZE"])
            self.defaultAudioFormatEntry = ft.Dropdown(label=i18n["defaultAudioFormat"], 
                                                        value=setting["DEFAULT_AUDIO_FORMAT"],
                                                        options=list(map(
                                                            ft.dropdown.Option,
                                                            SUPPORT_AUDIO_FORMAT
                                                        )))
            self.defaultAudioBitrateEntry = ft.TextField(label=i18n["defaultAudioBitrate"], 
                                                         value=setting["DEFAULT_AUDIO_BITRATE"])
            self.downloadEngineEntry = ft.TextField(label=i18n["downloadEngine"], 
                                                    value=setting["downloadEngine"])
            self.downloadEngineCommandEntry = ft.TextField(label=i18n["downloadEngineCommand"], 
                                                    value=setting["downloadEngineCommand"])
            self.aboutUserInfo = ft.Markdown(
                i18n["aboutUserInfo"],
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: page.launch_url(e.data),
            )
            myInfo = biliGetMyInfo()
            self.myBilibiliUser = ft.ListTile(
                leading=ft.CircleAvatar(
                    foreground_image_url=myInfo["face"]
                ),
                title=ft.Text(myInfo["name"])
            )
            # self.sessdataEntry = ft.TextField(
            #     label=i18n["sessdataEntry"],
            #     value=setting["SESSDATA"]
            # )
            # self.bilijctEntry = ft.TextField(
            #     label=i18n["bilijctEntry"],
            #     value=setting["BILI_JCT"]
            # )
            # self.buvid3Entry = ft.TextField(
            #     label=i18n["buvid3Entry"],
            #     value=setting["BUVID3"]
            # )
            # self.dedeuseridEntry = ft.TextField(
            #     label=i18n["dedeuseridEntry"],
            #     value=setting["DEDEUSERID"]
            # )
            self.QRLoginButton = ft.TextButton(
                text=i18n["QRLoginButton"],
                on_click=lambda _: biliQRLogin()
            )
        async def downloadAudio(bv,mode):
    # asyncio.set_event_loop(eventLoop)
            try:
                if setting["downloadEngine"] != "<Built-in>":
                    downloadCommand = setting["downloadEngineCommand"].replace('{downloadEngine}', setting["downloadEngine"])
                if (bv[:2:] == 'BV'):
                    v = video.Video(bvid=bv, credential=credential)
                elif (bv[:2:] == 'av' or bv[:2:] == 'AV'):
                    av = int(bv[2::])
                    v = video.Video(aid=av, credential=credential)
                info = await v.get_info() # Get Video info.
                # print(info)
                with open(f'{setting["CACHE_DIR"]}/bilimusic.video.info.{bv}.json', 'w+') as infoFile:
                    infoJsonString = json.dumps(info)
                    infoFile.write(infoJsonString)
                releaseYear = time.localtime(info["ctime"]).tm_year
                releaseTime = time.localtime(info["ctime"])
                releaseDate = time.strftime('%Y/%m/%d', releaseTime)
                pic_url = info['pic'] # Cover picture URL.
                header = {"User-Agent": setting['UA']}
                coverpic = requests.get(pic_url, headers=header) # Download Cover Image.
                # print(r.content)
                with open(f'{setting["CACHE_DIR"]}/bilimusic.cache.coverImage.{bv}', 'wb+') as file: # Write Cover Image to cache.
                    file.write(coverpic.content)
                cover.cover(bv, 
                            setting['COVER_RES'], 
                            setting['CACHE_DIR']) # Use cover.py to generate cover image.
                # print(info)
                # Artists
                if 'staff' in info:
                    Staff = info['staff'] # Staff
                    Artists = ""
                    for artist in Staff:
                        artistName = artist['name']
                        Artists += artistName + setting['ARTIST_DIVISION_CHAR']
                    Artists = Artists[:len(setting['ARTIST_DIVISION_CHAR']) * -1:]
                    # print(Artists)
                else:
                    Artists = info['owner']['name']
                url = await v.get_download_url(0) # Download url
                audio_name = str(info['title']) # Audio File Name.
                audio_title = audio_name # Audio Title.
                if "ugc_season" in info:
                    musicAlbum = info["ugc_season"]["title"]
                else:
                    musicAlbum = audio_title
                # global ILLEGAL_DIR_CHAR
                for char in ILLEGAL_DIR_CHAR:
                    audio_name = audio_name.replace(char, '_') # Replace illegal characters.
                if setting["downloadEngine"] != "<Built-in>":
                    download_dir = f'{setting["CACHE_DIR"]}/{bv}'
                    audio_url = url['dash']['audio'][0]['baseUrl'] # Audio URL
                    command = downloadCommand.replace('{url}', audio_url).replace('{output}', download_dir)
                    with os.popen(command):
                        pass
                else:
                    async with httpx.AsyncClient(headers=HEADERS) as sess:
                        audio_url = url['dash']['audio'][0]['baseUrl'] # Audio URL
                        resp = await sess.get(audio_url)
                        length = resp.headers.get('content-length') # Audio file length.
                        # Download audio.
                        with open(f'{setting["CACHE_DIR"]}/{bv}.m4s', 'wb') as f: 
                            process = 0
                            for chunk in resp.iter_bytes(1024):
                                if not chunk:
                                    break
                                process += len(chunk)
                                f.write(chunk)
                if os.path.exists(f'{setting["CACHE_DIR"]}/{bv}.m4s'):
                    if mode[0] == 'mp3':
                        ffmpeg_command = setting["decodeCommand"].replace('{decoder}', setting["FFMPEG"]).replace('{input}', f'"{setting["CACHE_DIR"]}/{bv}.m4s"').replace('{bitrate}', mode[1]).replace('{output}', f'"{setting["DOWNLOAD_DIR"]}/{audio_name}.mp3"')
                        ffmpeg_command = ffmpeg_command.replace('{decodelib}', setting["mp3Decoder"])
                        # ffmpeg_command = f'{setting["FFMPEG"]} -i "{setting["CACHE_DIR"]}/{audio_name}.m4s" -y -acodec libmp3lame -b:a {mode[1]} "{setting["DOWNLOAD_DIR"]}/{audio_name}.mp3"'
                    elif mode[0] == 'flac':
                        ffmpeg_command = setting["decodeCommand"].replace('{decoder}', setting["FFMPEG"]).replace('{input}', f'"{setting["CACHE_DIR"]}/{bv}.m4s"').replace('{bitrate}', mode[1]).replace('{output}', f'"{setting["DOWNLOAD_DIR"]}/{audio_name}.flac"')
                        ffmpeg_command = ffmpeg_command.replace('{decodelib}', setting["flacDecoder"])
                    print(ffmpeg_command)
                    with os.popen(ffmpeg_command):# Use ffmpeg to transcoding audio."""
                        pass
                    # Edit by EasyID3.
                    if mode[0] == 'mp3':
                        musicFile = EasyID3(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}')
                        musicFile["title"] = audio_title
                        musicFile["artist"] = Artists
                        musicFile["website"] = f'https://www.bilibili.com/video/{bv}'
                        musicFile["date"] = releaseDate
                        musicFile["album"] = musicAlbum
                    if mode[0] == 'flac':
                        musicFile = mutagen.flac.FLAC(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}')
                        musicFile.tags = mutagen.id3.ID3()
                        musicFile.save()
                        musicFile = mutagen.File(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}', easy = True)
                        # musicFile.add_tags()
                        musicFile["title"] = audio_title
                        musicFile["artist"] = Artists
                        musicFile["website"] = f'https://www.bilibili.com/video/{bv}'
                        musicFile["date"] = releaseDate
                        musicFile["album"] = musicAlbum
                        # print(f'musicFile: {musicFile}')
                    # musicFile.save()
                    musicFile.save()
                    coverFile = open(f'{setting["CACHE_DIR"]}/bilimusic.cache.cover.{bv}.jpg', 'rb').read()
                    if mode[0] == 'mp3':
                        musicFileMP3 = mutagen.mp3.MP3(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}', ID3 = ID3)
                        musicFileMP3.tags.add(APIC(encoding = 3,
                                                mime = 'image/jpg',
                                                type = 3,
                                                desc = u'Cover',
                                                data = coverFile))
                        musicFileMP3.save(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}')
                    if mode[0] == 'flac':
                        musicFileFLAC = mutagen.File(f'{setting["DOWNLOAD_DIR"]}/{audio_name}.{mode[0]}')
                        flacCoverImage = mutagen.flac.Picture()
                        flacCoverImage.type = 3
                        flacCoverImage.desc = 'front cover'
                        flacCoverImage.data = coverFile
                        musicFileFLAC.add_picture(flacCoverImage)
                        musicFileFLAC.save()
                    # Delete Cache. 
                    if setting["cacheAutoDelete"]:
                        os.remove(f'{setting["CACHE_DIR"]}/bilimusic.cache.coverImage.{bv}') 
                        os.remove(f'{setting["CACHE_DIR"]}/bilimusic.cache.cover.{bv}.jpg')
                        os.remove(f'{setting["CACHE_DIR"]}/{bv}.m4s')
                        os.remove(f'{setting["CACHE_DIR"]}/bilimusic.video.info.{bv}.json')
                    showSnackBar(message = f'{bv} {audio_name} {i18n["downloadFinished"]}')
                    return 0
                    # os._exit(0)
                else:
                    raise OSError(f"File {setting['CACHE_DIR']}/{bv}.m4s does not exists.")
            except:
                Error = traceback.format_exc()
                showMessage(title = i18n["error"], message = f'{bv} {i18n["downloadFailed"]} {Error}')
                print(f'{bv} 下载失败。\n错误信息：{Error}')
                return 1
                # os._exit(1)
        def preDownload(self):
        # global bvEntry, formatMenu, bitrateEntry
            bv = str(self.bvEntry.value)
            audio_format = str(self.formatMenu.value)
            bit_rate = str(self.bitrateEntry.value)
            if bv == '' or not(bv[:2:] == 'BV' or bv[:2:] == 'av' or bv[:2:] == 'AV'):
                showMessage(title=i18n["error"], message=f'{i18n["invalidBV"]} {bv}')
                return 0
            showSnackBar(f'{i18n["nowDownloading"]} {bv}')
            downloadCoroutine = downloadAudio(bv, (audio_format, bit_rate))
            newLoop = asyncio.new_event_loop()
            lockThread = threading.Thread(target=self.setEventLoop, args=(newLoop, ))
            lockThread.start()
            asyncio.run_coroutine_threadsafe(downloadCoroutine, newLoop)
        self.mainPage()
        self.otherLibrary()
        settings(self)
        # self.about()
        self.titleImage = ft.Image(
                src='bilimusic.svg',
                width=200,
                height=200,
                fit=ft.ImageFit.CONTAIN
        )
        self.MainPage = ft.View(
            "/",
            [
                ft.AppBar(
                    leading=self.titleImage,
                    leading_width=40,
                    title=ft.Text(i18n["name"]),
                    actions=[
                        ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            tooltip=i18n["settings"],
                            on_click=lambda _:page.go('/settings')
                        ),
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(icon=ft.icons.INFO, 
                                                text=i18n["about"],
                                                on_click=lambda _:page.go('/about')),
                                ft.PopupMenuItem(text=i18n["otherLib"],
                                                on_click=lambda _:page.go('/otherlib'))
                            ]
                        ),
                    ]
                ),
                self.bvEntry,
                self.formatMenu,
                self.bitrateEntry,
                ft.FilledButton(text=i18n["ok"], on_click=lambda _:preDownload(self))
            ],
            scroll='AUTO'
        )
        self.AboutPage = ft.View(
            "/about",
            [
                ft.AppBar(
                    title=ft.Text(i18n["about"])
                ),
                ft.Text(
                    f'bilimusic\n{i18n["copyright"]}'
                ),
                ft.Text(
                    LICENSE_GPLV3
                )
            ],
            scroll='AUTO'
        )
        self.otherLibPage = ft.View(
            "/otherlib",
            [
                ft.AppBar(
                    title=ft.Text(i18n["otherLib"])
                ),
                ft.Text(
                    self.otherLibLicenseText
                )
            ],
            scroll='AUTO'
        )
        self.settingPage = ft.View(
            "/settings",
            [
                ft.AppBar(
                    title=ft.Text(i18n["settings"])
                ),
                self.languageMenu,
                self.darkModeSwitch,
                self.downloadDirEntry,
                self.cacheDirEntry,
                self.cacheAutoDeleteButton,
                self.decoderBinEntry,
                self.decodeCommandEntry,
                self.mp3DecoderEntry,
                self.flacDecoderEntry,
                self.artistDivisionCharEntry,
                self.coverResText,
                self.coverResSlider,
                self.UAEntry,
                self.downloadChunkSizeText,
                self.downloadChunkSizeSlider,
                self.defaultAudioFormatEntry,
                self.defaultAudioBitrateEntry,
                self.downloadEngineEntry,
                self.downloadEngineCommandEntry,
                self.aboutUserInfo,
                self.myBilibiliUser,
                # self.sessdataEntry,
                # self.bilijctEntry,
                # self.buvid3Entry,
                # self.dedeuseridEntry,
                self.QRLoginButton,
                ft.FilledButton(
                    text=i18n["ok"], 
                    on_click=lambda _:enableSettings(self)
                )
            ],
            scroll='AUTO'
        )
        def changeRoute(route):
            page.views.clear()
            page.views.append(self.MainPage)
            if page.route == '/about':
                page.views.append(self.AboutPage)
            if page.route == '/otherlib':
                page.views.append(self.otherLibPage)
            if page.route == '/settings':
                page.views.append(self.settingPage)
            page.update()
        def viewPop(view):
            page.views.pop()
            topView = page.views[-1]
            page.go(topView.route)
        page.on_route_change = changeRoute
        page.on_view_pop = viewPop
        page.go(page.route)
    def mainPage(self):
        # titleContainer = ft.Container()
        self.bvEntry = ft.TextField(label=i18n["bvEntry"])
        self.formatMenu = ft.Dropdown(label=i18n["audioFormat"],
                                     value=setting["DEFAULT_AUDIO_FORMAT"],
                                     options=list(map(
                                        ft.dropdown.Option,
                                        SUPPORT_AUDIO_FORMAT
                                     )))
        self.bitrateEntry = ft.TextField(label=i18n["audioBitrate"],
                                         value=setting["DEFAULT_AUDIO_BITRATE"])
    def setEventLoop(self, eventLoop):
        self.eventLoop = eventLoop
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.run_forever()
    def otherLibrary(self):
        self.otherLibLicenseText = bilimusic_data.getData('LICENSE_OTHER_LIBRARY', 'str')
        if self.otherLibLicenseText == None:
            self.otherLibLicenseText = '加载失败，请打开同目录下的 LICENSE_OTHER_LIBRARY 文件查看第三方库的许可证信息。'
if __name__ == '__main__':
    # GUIForm = bilimusicApp()
    ft.app(target=bilimusicApp, assets_dir='bilimusic_data')
    #bv = input("bvid: ") # Input Bvid.