import discord.errors
from discord import FFmpegPCMAudio
import youtube_dl
import urllib.parse, urllib.request, re
from ytmusicapi import YTMusic
from discord.utils import get
import math

ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
servers = {}
ytmusic = YTMusic("headers_auth.json")


class BotServers:
    def __init__(self, server):
        self.server = server
        self.queue = []
        self.curnum = 0
        self.is_looping = False
        self.is_looping_queue = False
        self.vc_channel = None
        self.messagechannel = None
        self.is_playing = False
        self.ytmusicqueue = []


async def get_song(obj, ctx, client, song):#WILL ADD SPOTIFY SUPPORT LATER
    thing = re.search("https://www.youtube.com/", song)
    if thing is None:
        link = urllib.parse.urlencode({'search_query': song})
        content = urllib.request.urlopen('http://www.youtube.com/results?' + link)
        searchresult = re.findall(r'/watch\?v=(.{11})', content.read().decode())
        url = ('http://www.youtube.com/watch?v=' + searchresult[0])
        with youtube_dl.YoutubeDL(ydl_opts) as YDL:
            info = YDL.extract_info(url, download=False)
        obj.queue.append(info)
    else:
        with youtube_dl.YoutubeDL(ydl_opts) as YDL:
            info = YDL.extract_info(song, download=False)
        obj.queue.append(info)
    ytmusicthing = ytmusic.search(info["title"])
    obj.ytmusicqueue.append(ytmusicthing[0]["videoId"])
    await ctx.send(f"Added {info['title']} to queue")
    if not obj.is_playing:
        play_song(obj, client)


def play_song(obj, client):
    if len(obj.queue) < obj.curnum:
        return 0
    else:
        obj.is_playing = True
        voice = get(client.voice_clients)
        voice.play(FFmpegPCMAudio(obj.queue[obj.curnum]["url"], **FFMPEG_OPTIONS), after=lambda x: aftersong(obj, client))


def aftersong(obj, client):
    obj.is_playing = False
    if not obj.is_looping:
        obj.curnum += 1
    elif obj.is_looping_queue and obj.curnum == len(obj.queue):
        obj.curnum = 0
    play_song(obj, client)


async def downloader(ctx, song):
    link = urllib.parse.urlencode({'search_query': song})
    content = urllib.request.urlopen('http://www.youtube.com/results?' + link)
    searchresult = re.findall(r'/watch\?v=(.{11})', content.read().decode())
    url = ('http://www.youtube.com/watch?v=' + searchresult[0])
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    await ctx.send("Downloaded")


async def get_lyrics(ctx, obj):
    musicid = obj.ytmusicqueue[obj.curnum]
    thing = ytmusic.get_watch_playlist(musicid)
    lyricid = thing["lyrics"]
    if lyricid:
        lyrs = ytmusic.get_lyrics(str(lyricid))
        lyrics = lyrs["lyrics"]
        try:
            await ctx.send("```" + lyrics + "```")
        except discord.errors.HTTPException:
            temp = lyrics[math.ceil(len(lyrics) / 2):len(lyrics) - 1]
            templyrics = list(lyrics)
            del templyrics[math.ceil(len(lyrics) / 2):len(lyrics) - 1]
            await ctx.send("```" + "".join(templyrics) + "```")
            await ctx.send("```" + temp + "```")
    else:
        await ctx.send("Lyrics don't exist for this song :P")