# ############################################################# 
# Bilidown Main                                                 
# Copyright (C) 2023 cmderli. This program is a free software.
# #############################################################
VERSION = 'bilidown v0.1'
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
from bilibili_api import video, Credential, HEADERS # Need bilibili-api to get Video Info and download Audio.
import httpx
import os
import requests # Need request to download cover image.
# import imghdr
from PIL import Image# Need Pillow to make Music Cover Image.
import tkinter, tkinter.ttk, tkinter.font
from tkinter import messagebox, scrolledtext, filedialog
import cover
import json
import threading
import mutagen # Needs mutagen to edit music's id3 info.
import mutagen.flac
import mutagen.mp3
import mutagen.id3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
# import mutagen.wave
import traceback
# bv test : BV1sM4y1V7x1
ILLEGAL_DIR_CHAR = ['<', '|', '>', '\\', '/', ':', '"', '*', '?'] # There is The Illegal Directory Characters.
# DOWNLOAD_DIR = os.getcwd() # Download Directory here.
# FFMPEG = 'ffmpeg' # ffmpeg here 
# HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"} # User-Agent Here.
# ARTIST_DIVISION_CHAR = '/'
SUPPORT_AUDIO_FORMAT = ('mp3', 'flac')
CWD = os.getcwd()
setting = {
    "DOWNLOAD_DIR": CWD,
    "CACHE_DIR": CWD+"/.bilidown_cache",
    "FFMPEG": "ffmpeg",
    "ARTIST_DIVISION_CHAR": "/",
    "COVER_RES": 1024,
    "UA": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "FONT": "",
    "DOWNLOAD_CHUNK_SIZE": 1024,
    "DEFAULT_AUDIO_FORMAT": "mp3",
    "DEFAULT_AUDIO_BITRATE": "320k"
}
if not(os.path.exists('bilidown.SETTINGS')):
    if not(os.path.exists(setting['CACHE_DIR'])):
        os.mkdir(setting['CACHE_DIR'])
    with open('bilidown.SETTINGS', 'w+', encoding='utf-8') as f:
        jsonString = json.dumps(setting)
        f.write(jsonString)
with open('bilidown.SETTINGS', 'r', encoding='utf-8') as f:
    jsonString = f.read()
    setting = json.loads(jsonString)
    # print(setting)
if not(os.path.exists(setting['CACHE_DIR'])):
    setting['CACHE_DIR'] = CWD+'/.bilidown_cache'
    with open('bilidown.SETTINGS', 'w+', encoding='utf-8') as f:
        jsonString = json.dumps(setting)
        f.write(jsonString)
if os.path.exists('LICENSE'): # Load GPL v3.
    readLICENSE_GPLV3 = open('LICENSE', 'r', encoding='utf-8').read()
    if readLICENSE_GPLV3 == '':
        LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
    else:
        LICENSE_GPLV3 = readLICENSE_GPLV3
else:
    if not(os.path.exists(f'{setting["CACHE_DIR"]}/bilidown.license.gplv3.cache')):
        try:
            header = {"User-Agent": setting['UA']}
            gplv3 = requests.get('https://www.gnu.org/licenses/gpl-3.0.txt', headers=header) # https://www.gnu.org/licenses/gpl-3.0.txt
            LICENSE_GPLV3 = gplv3.content
            with open(f'{setting["CACHE_DIR"]}/bilidown.license.gplv3.cache', 'w+', encoding='utf-8') as licenseCacheFile:
                licenseCacheFile.write(LICENSE_GPLV3.decode('utf-8'))
        except:
            # print(Error)
            LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
    else:
        readLICENSE_GPLV3 = open(f'{setting["CACHE_DIR"]}/bilidown.license.gplv3.cache', 'r', encoding='utf-8').read()
        if readLICENSE_GPLV3 == '':
            LICENSE_GPLV3 = '加载错误，请访问 https://www.gnu.org/licenses/gpl-3.0.txt 查看 GNU 通用公共许可证 第三版 的原文。'
        else:
            LICENSE_GPLV3 = readLICENSE_GPLV3
class bilidownApp:
    def __init__(self):
        # GUI Interface
        # I DON'T WANT TO WRITE COMMENTS.
        # 我不想写注释了...
        self.root = tkinter.Tk()
        self.fontFamilies = tkinter.font.families()
        # print(len(self.fontFamilies))
        self.root.title('bilibili音乐下载器-bilidown')
        self.root.geometry('800x600')
        self.root_menu = tkinter.Menu(self.root)
        self.root_menu.add_command(label='设置', command = self.settings)
        self.root_menu.add_command(label='关于', command = self.about)
        self.root_menu.add_command(label='第三方库', command = self.otherLibrary)
        self.root.config(menu = self.root_menu)
        title = tkinter.Label(self.root, 
                            text='\nbilibili音乐下载器',
                            font=(setting["FONT"],40,'normal'))
        self.textEntry = tkinter.StringVar()
        self.textEntry.set('在此输入BV号')
        self.bvEntry = tkinter.Entry(self.root, 
                                textvariable=self.textEntry, 
                                font=(setting["FONT"], 
                                20, 
                                'normal'))
        defaultAudioFormat = tkinter.StringVar(value=setting["DEFAULT_AUDIO_FORMAT"])
        self.formatTitle = tkinter.Label(self.root, 
                                    text='音乐格式', 
                                    font=(setting["FONT"], 
                                    20, 
                                    'normal'))
        self.formatMenu = tkinter.ttk.Combobox(self.root, 
                                               textvariable=defaultAudioFormat, 
                                               values=('mp3', 'flac'), 
                                               font=(setting["FONT"],20,'normal'))
        defaultAudioBitrate = tkinter.StringVar(value=setting["DEFAULT_AUDIO_BITRATE"])
        bitrateTitle = tkinter.Label(self.root, 
                                     text='音频质量\nflac请填0 ~ 8压缩等级，\nmp3填码率（例如320k）',
                                     font=(setting["FONT"],20,'normal'))
        self.bitrateEntry = tkinter.Entry(self.root, 
                                          textvariable=defaultAudioBitrate, 
                                          font=(setting["FONT"], 20, 'normal'))
        self.okButton = tkinter.Button(self.root, 
                                text = '下载', 
                                font = (setting["FONT"], 20, 'normal'), 
                                command=self.preDownload)
        title.pack()
        self.bvEntry.pack()
        self.formatTitle.pack(pady=10)
        self.formatMenu.pack()
        bitrateTitle.pack()
        self.bitrateEntry.pack()
        self.okButton.pack()
        self.root.mainloop()
    def setEventLoop(self, eventLoop):
        self.eventLoop = eventLoop
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.run_forever()
    def preDownload(self):
        # global bvEntry, formatMenu, bitrateEntry
        bv = str(self.bvEntry.get())
        audio_format = str(self.formatMenu.get())
        bit_rate = str(self.bitrateEntry.get())

        if bv == '' or bv == '在此输入BV号' or not(bv[:2:] == 'BV' or bv[:2:] == 'av'):
            messagebox.showerror(title='错误', message=f'无效的bv号 {bv}')
            return 0
        if audio_format not in SUPPORT_AUDIO_FORMAT:
            messagebox.showerror(title='错误', message=f'不支持的文件格式 {audio_format}')
            return 0
        if audio_format == 'mp3':
            if bit_rate[-1::] != 'k':
                messagebox.showerror(title='错误', message=f'不支持的码率 {bit_rate}')
                return 0
            if int(bit_rate[:-1:]) > 320 or int(bit_rate[:-1:]) < 32:
                messagebox.showerror(title='错误', message=f'不支持的码率 {bit_rate}')
                return 0
        elif audio_format == 'flac':
            if len(bit_rate) != 1:
                messagebox.showerror(title='错误', message=f'不支持的压缩等级 {bit_rate}')
                return 0
            if bit_rate == '9':
                messagebox.showerror(title='错误', message=f'不支持的压缩等级 {bit_rate}')
                return 0
        # Download(bv, (audio_format, bit_rate))
        downloadCoroutine = self.downloadAudio(bv, (audio_format, bit_rate))
        newLoop = asyncio.new_event_loop()
        lockThread = threading.Thread(target=self.setEventLoop, args=(newLoop, ))
        lockThread.start()
        asyncio.run_coroutine_threadsafe(downloadCoroutine, newLoop)
        # asyncio.get_event_loop().run_until_complete(downloadAudio(bv, (audio_format, bit_rate)))
    async def downloadAudio(self, bv,mode):
    # asyncio.set_event_loop(eventLoop)
        try:
            if (bv[:2:] == 'BV'):
                v = video.Video(bvid=bv)
            elif (bv[:2:] == 'av'):
                av = int(bv[2::])
                v = video.Video(aid=av)
            info = await v.get_info() # Get Video info.
            # print(info)
            with open(f'{setting["CACHE_DIR"]}/bilidown.video.info.{bv}.json', 'w+') as infoFile:
                infoJsonString = json.dumps(info)
                infoFile.write(infoJsonString)
            releaseYear = time.localtime(info["ctime"]).tm_year
            releaseTime = time.localtime(info["ctime"])
            releaseDate = time.strftime('%Y/%m/%d', releaseTime)
            pic_url = info['pic'] # Cover picture URL.
            header = {"User-Agent": setting['UA']}
            coverpic = requests.get(pic_url, headers=header) # Download Cover Image.
            # print(r.content)
            with open(f'{setting["CACHE_DIR"]}/bilidown_CACHE_coverImage_{bv}', 'wb+') as file: # Write Cover Image to cache.
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
            async with httpx.AsyncClient(headers=HEADERS) as sess:
                audio_url = url['dash']['audio'][0]['baseUrl'] # Audio URL
                resp = await sess.get(audio_url)
                length = resp.headers.get('content-length') # Audio file length.
                # Download audio.
                with open(f'{setting["CACHE_DIR"]}/{audio_name}.m4s', 'wb') as f: 
                    process = 0
                    for chunk in resp.iter_bytes(1024):
                        if not chunk:
                            break
                        process += len(chunk)
                        f.write(chunk)
            if os.path.exists(f'{setting["CACHE_DIR"]}/{audio_name}.m4s'):
                if mode[0] == 'mp3':
                    ffmpeg_command = f'{setting["FFMPEG"]} -i "{setting["CACHE_DIR"]}/{audio_name}.m4s" -y -acodec libmp3lame -b:a {mode[1]} "{setting["DOWNLOAD_DIR"]}/{audio_name}.mp3"'
                elif mode[0] == 'flac':
                    ffmpeg_command = f'{setting["FFMPEG"]} -i "{setting["CACHE_DIR"]}/{audio_name}.m4s" -y -acodec flac -compression_level {mode[1]} "{setting["DOWNLOAD_DIR"]}/{audio_name}.flac"'
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
                coverFile = open(f'{setting["CACHE_DIR"]}/bilidown_CACHE_cover_{bv}.jpg', 'rb').read()
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
                # os.remove(f'{setting["CACHE_DIR"]}/bilidown_CACHE_coverImage_{bv}') 
                # os.remove(f'{setting["CACHE_DIR"]}/bilidown_CACHE_cover_{bv}.jpg')
                # os.remove(f'{setting["CACHE_DIR"]}/{audio_name}.m4s')
                messagebox.showinfo(title = '信息', message = f'{bv} {audio_name} 下载成功。')
                return 0
                # os._exit(0)
            else:
                raise OSError(f"File {setting['DOWNLOAD_DIR']}/{audio_name}.m4s does not exists.")
        except:
            Error = traceback.format_exc()
            messagebox.showerror(title = '错误', message = f'{bv} 下载失败。\n错误信息：{Error}')
            print(f'{bv} 下载失败。\n错误信息：{Error}')
            return 1
            # os._exit(1)
    def downloadDirSet(self):
        dirname = filedialog.askdirectory()
        print(dirname)
        if dirname != '':
            self.DownloadDir.set(value=dirname)
    def cacheDirSet(self):
        dirname = filedialog.askdirectory()
        print(dirname)
        if dirname != '':
            self.CacheDir.set(value=dirname)
    def settings(self):
        # global self.setting_win
        self.setting_win = tkinter.Toplevel()
        self.setting_win.title('设置')
        self.setting_win.geometry('400x800')
        global setting
        downloadDirTitle = tkinter.Label(self.setting_win, 
                                        text='下载目录', 
                                        font=(setting["FONT"], 
                                        15, 
                                        'normal'))
        downloadDirFrame = tkinter.Frame(self.setting_win)
        downloadDirSetButton = tkinter.Button(downloadDirFrame,text='选择', 
                                              font=(setting["FONT"], 
                                              15, 
                                              'normal'),
                                              command=self.downloadDirSet)
        self.DownloadDir = tkinter.StringVar(value=setting['DOWNLOAD_DIR'])
        cacheDirTitle = tkinter.Label(self.setting_win, 
                                    text='缓存文件目录', 
                                    font=(setting["FONT"], 
                                    15, 
                                    'normal'))
        cacheDirFrame = tkinter.Frame(self.setting_win)
        self.CacheDir = tkinter.StringVar(value=setting['CACHE_DIR']) # CACHE_DIR
        # global cacheDirEntry, downloadDirEntry, ffmpegEntry, ADCEntry, CREntry, UAEntry, FontEntry, downloadChunkSizeEntry
        self.cacheDirEntry = tkinter.Entry(cacheDirFrame, 
                                    textvariable=self.CacheDir, 
                                    font=(setting["FONT"], 
                                    15, 
                                    'normal'))
        cacheDirSetButton = tkinter.Button(cacheDirFrame,text='选择', 
                                              font=(setting["FONT"], 
                                              15, 
                                              'normal'),
                                              command=self.cacheDirSet)
        self.downloadDirEntry = tkinter.Entry(downloadDirFrame, 
                                        textvariable=self.DownloadDir, 
                                        font=(setting["FONT"], 
                                        15, 
                                        'normal'))
        ffmpegTitle = tkinter.Label(self.setting_win, 
                                    text='FFMPEG', 
                                    font=(setting["FONT"], 
                                    15, 
                                    'normal'))
        ffmpeg = tkinter.StringVar(value=setting['FFMPEG'])
        self.ffmpegEntry = tkinter.Entry(self.setting_win, 
                                    textvariable=ffmpeg, 
                                    font=(setting["FONT"], 
                                    15, 
                                    'normal'))
        ADCTitle = tkinter.Label(self.setting_win, 
                                text='艺术家分隔符', 
                                font=(setting["FONT"], 
                                15, 
                                'normal')) # "ARTIST_DIVISION_CHAR"
        aDC = tkinter.StringVar(value=setting['ARTIST_DIVISION_CHAR'])
        self.ADCEntry = tkinter.Entry(self.setting_win, 
                                textvariable=aDC, 
                                font=(setting["FONT"], 
                                15, 
                                'normal'))
        CRTitle = tkinter.Label(self.setting_win, 
                                text='封面长宽（像素）', 
                                font=(setting["FONT"], 
                                15, 
                                'normal')) # "COVER_RES"
        cR = tkinter.StringVar(value=setting['COVER_RES'])
        self.CREntry = tkinter.Entry(self.setting_win, 
                                textvariable=cR, 
                                font=(setting["FONT"], 
                                15, 
                                'normal'))
        UATitle = tkinter.Label(self.setting_win, 
                                text='UA', 
                                font=(setting["FONT"], 
                                15, 
                                'normal')) # "UA"
        uA = tkinter.StringVar(value=setting['UA'])
        self.UAEntry = tkinter.Entry(self.setting_win, 
                                textvariable=uA, 
                                font=(setting["FONT"], 
                                15, 
                                'normal'))
        FontTitle = tkinter.Label(self.setting_win, 
                                text='字体', 
                                font=(setting["FONT"], 
                                15, 
                                'normal')) # "UA"
        # UIFont = tkinter.StringVar(value=setting["FONT"])
        # print(setting["FONT"])
        # print(self.fontFamilies)
        # print(type(self.fontFamilies))
        self.FontEntry = tkinter.ttk.Combobox(self.setting_win, 
                                              # textvariable=UIFont, 
                                              values=self.fontFamilies,
                                              font=(setting["FONT"], 
                                              15, 
                                              'normal'))
        self.FontEntry.set(setting["FONT"])
        downloadChunkSize = tkinter.StringVar(value=setting["DOWNLOAD_CHUNK_SIZE"]) # "DOWNLOAD_CHUNK_SIZE"
        downloadChunkSizeTitle = tkinter.Label(self.setting_win, 
                                            text='下载块大小(字节)',
                                            font=(setting["FONT"], 15, 'normal'))
        self.downloadChunkSizeEntry = tkinter.Entry(self.setting_win, 
                                            textvariable=downloadChunkSize, 
                                            font=(setting["FONT"], 15, 'normal'))
        defaultAudioFormat = tkinter.StringVar(value=setting["DEFAULT_AUDIO_FORMAT"]) # "DEFAULT_AUDIO_FORMAT"
        defaultAudioFormatTitle = tkinter.Label(self.setting_win, 
                                            text='默认音频文件扩展名',
                                            font=(setting["FONT"], 15, 'normal'))
        self.defaultAudioFormatEntry = tkinter.Entry(self.setting_win, 
                                            textvariable=defaultAudioFormat, 
                                            font=(setting["FONT"], 15, 'normal'))
        defaultAudioBitrate = tkinter.StringVar(value=setting["DEFAULT_AUDIO_BITRATE"]) # "DEFAULT_AUDIO_BITRATE" Default Audio Bitrate.
        defaultAudioBitrateTitle = tkinter.Label(self.setting_win, 
                                            text='默认码率或压缩等级',
                                            font=(setting["FONT"], 15, 'normal'))
        self.defaultAudioBitrateEntry = tkinter.Entry(self.setting_win, 
                                            textvariable=defaultAudioBitrate, 
                                            font=(setting["FONT"], 15, 'normal'))
        OKButton = tkinter.Button(self.setting_win, 
                                text='确定', 
                                font=(setting["FONT"], 
                                15, 
                                'normal'), 
                                command=self.enableSettings)
        downloadDirTitle.pack()
        downloadDirFrame.pack()
        self.downloadDirEntry.pack(side='left')
        downloadDirSetButton.pack(side='right')
        cacheDirTitle.pack()
        # self.cacheDirEntry.pack()
        cacheDirFrame.pack()
        self.cacheDirEntry.pack(side='left')
        cacheDirSetButton.pack(side='right')
        ffmpegTitle.pack()
        self.ffmpegEntry.pack()
        ADCTitle.pack()
        self.ADCEntry.pack()
        CRTitle.pack()
        self.CREntry.pack()
        UATitle.pack()
        self.UAEntry.pack()
        FontTitle.pack()
        self.FontEntry.pack()
        downloadChunkSizeTitle.pack()
        self.downloadChunkSizeEntry.pack()
        defaultAudioFormatTitle.pack()
        self.defaultAudioFormatEntry.pack()
        defaultAudioBitrateTitle.pack()
        self.defaultAudioBitrateEntry.pack()
        OKButton.pack()
    def enableSettings(self):
        # Get settings in setup window and write settings.
        # global setting
        cache_dir = self.cacheDirEntry.get()
        download_dir = self.downloadDirEntry.get()
        if cache_dir[-1::] == '\\' or cache_dir[-1::] == '/':
            cache_dir = cache_dir[:-1:]
        if download_dir[-1::] == '\\' or download_dir[-1::] == '/':
            download_dir = download_dir[:-1:]
        if not(os.path.exists(cache_dir)):
            try:
                os.mkdir(cache_dir)
            except:
                messagebox.showerror(title='错误', message=f'创建目录 {cache_dir} 失败。')
                return 0
        if not(os.path.exists(download_dir)):
            try:
                os.mkdir(download_dir)
            except:
                messagebox.showerror(title='错误', message=f'创建目录 {download_dir} 失败。')
                return 0
        if str(self.downloadChunkSizeEntry.get()).isdecimal():
            downloadChunkSize = int(self.downloadChunkSizeEntry.get())
            if downloadChunkSize <= 0:
                messagebox.showerror(title='错误', 
                                    message=f'下载块大小 {downloadChunkSize} 小于等于0。')
                return 0
        else:
            messagebox.showerror(title='错误', 
                                message=f'下载块大小 {self.downloadChunkSizeEntry.get()} 不是十位整数数字。')
        if self.defaultAudioFormatEntry.get() in SUPPORT_AUDIO_FORMAT:
            if self.defaultAudioFormatEntry.get() == 'mp3':
                if self.defaultAudioBitrateEntry.get()[-1::] != 'k':
                    messagebox.showerror(title='错误', message=f'不支持的码率 {self.defaultAudioBitrateEntry.get()}')
                    return 0
                if int(self.defaultAudioBitrateEntry.get()[:-1:]) > 320 or int(self.defaultAudioBitrateEntry.get()[:-1:]) < 32:
                    messagebox.showerror(title='错误', message=f'不支持的码率 {self.defaultAudioBitrateEntry.get()}')
                    return 0
                defaultAudioFormat = self.defaultAudioFormatEntry.get()
                defaultAudioBitrate = self.defaultAudioBitrateEntry.get()
            elif self.defaultAudioFormatEntry.get() == 'flac':
                if len(self.defaultAudioBitrateEntry.get()) != 1:
                    messagebox.showerror(title='错误', message=f'不支持的压缩等级 {self.defaultAudioBitrateEntry.get()}')
                    return 0
                if self.defaultAudioBitrateEntry.get() == '9':
                    messagebox.showerror(title='错误', message=f'不支持的压缩等级 {self.defaultAudioBitrateEntry.get()}')
                    return 0
                defaultAudioFormat = self.defaultAudioFormatEntry.get()
                defaultAudioBitrate = self.defaultAudioBitrateEntry.get()
        else:
            messagebox.showerror(title='错误', message=f'不支持的格式 {self.defaultAudioFormatEntry.get()}')
            return 0
        setting = {
            "DOWNLOAD_DIR": download_dir,
            "CACHE_DIR": cache_dir,
            "FFMPEG": self.ffmpegEntry.get(),
            "ARTIST_DIVISION_CHAR": self.ADCEntry.get(),
            "COVER_RES": int(self.CREntry.get()),
            "UA": self.UAEntry.get(),
            "FONT": self.FontEntry.get(), 
            "DOWNLOAD_CHUNK_SIZE": downloadChunkSize,
            "DEFAULT_AUDIO_FORMAT": defaultAudioFormat,
            "DEFAULT_AUDIO_BITRATE": defaultAudioBitrate
        }
        with open('bilidown.SETTINGS', 'w+', encoding='utf-8') as f:
            jsonString = json.dumps(setting)
            f.write(jsonString)
        self.setting_win.destroy()
    def about(self):
        about_win = tkinter.Tk()
        about_win.title('关于')
        about_win.geometry('640x480')
        _copyright = tkinter.Label(about_win, 
                                text=VERSION+COPYRIGHT, 
                                justify='left', 
                                font=(setting["FONT"], 10, 'normal'))
        _gplv3 = scrolledtext.ScrolledText(about_win)
        _gplv3.insert('0.0', LICENSE_GPLV3)
        _copyright.pack()
        _gplv3.pack(fill=tkinter.BOTH,expand=True)
        _gplv3.config(state=tkinter.DISABLED)
    def otherLibrary(self):
        about_win = tkinter.Tk()
        about_win.title('第三方库')
        about_win.geometry('800x600')
        if os.path.exists('LICENSE_OTHER_LIBRARY'):
            Text = open('LICENSE_OTHER_LIBRARY', 'r', encoding='utf-8').read()
        else:
            Text = '加载失败，请打开同目录下的 LICENSE_OTHER_LIBRARY 文件查看第三方库的许可证信息。'
        text = scrolledtext.ScrolledText(about_win)
        text.insert('0.0', Text)
        text.pack(fill=tkinter.BOTH,expand=True)
        text.config(state=tkinter.DISABLED)
if __name__ == '__main__':
    GUIForm = bilidownApp()
    #bv = input("bvid: ") # Input Bvid.