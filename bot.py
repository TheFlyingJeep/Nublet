import discord
from discord.ext import commands
import asyncio
import youtube_dl
from discord.utils import get
from discord import FFmpegPCMAudio
import urllib.parse, urllib.request, re
from random import randint
import requests
import bs4
import math
import json
import os
from ytmusicapi import YTMusic

client = commands.Bot(command_prefix='.')
uuid_cache = {}
songq = []
value = 0
looped = False
loopedqueue = False
is_playing = False
botchannel = None
leave = False
ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
blank = ""
lives = 0
active = False
guessed = ""
guessedarr = []
gameon = False
_guess = ""
__hangman = []
blankarr = []
styles = ["water", "fire", "air", "earth"]
turn = 0
lives1 = 0
lives2 = 0
burn1 = False
burn2 = False
sleep1 = False
sleep2 = False
freeze1 = False
freeze2 = False
earth1 = 0
earth2 = 0
duelactive = False


with open("token.txt", "r") as t:
    token = t.read()
with open("api_key.txt", "r") as api:
    api_key = api.read()


@client.event
async def on_ready():
    print("Teky is a nublet")


@client.command()
async def register(ctx, ign):
    player = requests.get("https://api.mojang.com/users/profiles/minesraft/"+ign)
    player = player.json()
    uuid = player["id"]
    with open("registered.txt", "r") as filep:
        contents = filep.read().split()
        if contents.count(uuid) == 0:
            with open("registered.txt", "a") as fileps:
                fileps.write("\n"+uuid)
                fileps.close()
                await ctx.send("Registered")


@client.command(aliases=["duelslb"])
async def duelsleaderboard(ctx):
    duels = ["sw", "bridge", "bow", "uhc", "sumo", "classic", "op", "combo"]
    leaderboard = []
    names = []
    templb = []
    async with ctx.typing():
        try:
            mode = ctx.message.content.split()[1]
        except IndexError:
            with open("registered.txt", "r") as players:
                uuids = players.read().split()
                for uuid in uuids:
                    duelstats = \
                    requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}").json()["player"]["stats"][
                        "Duels"]
                    wins = duelstats["wins"] if "wins" in duelstats else 0
                    leaderboard.append(wins)
                    templb.append(wins)
                    names.append(wins)
                leaderboard.sort()
                templb.sort()
                for val in uuids:
                    temp = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={val}").json()["player"]
                    name = temp["displayname"]
                    tempw = temp["stats"]["Duels"]["wins"] if "wins" in temp["stats"][
                        "Duels"] else 0
                    ind = templb.index(tempw)
                    names[ind] = name
                    templb[ind] = -1
                players.close()
                lb = leaderboard[::-1]
                names = names[::-1]
                out = "```Leaderboard for total duel wins\n"

                def titles(number):
                    if number < 100:
                        return "Not enough wins"
                    elif 100 <= number < 200:
                        ran = math.ceil((number - 100) / 20)
                        return "Rookie " + str(ran)
                    elif 200 <= number < 500:
                        ran = math.ceil((number - 200) / 60)
                        return "Iron " + str(ran)
                    elif 500 <= number < 1000:
                        ran = math.ceil((number - 500) / 100)
                        return "Gold " + str(ran)
                    elif 1000 <= number < 2000:
                        ran = math.ceil((number - 1000) / 200)
                        return "Diamond " + str(ran)
                    elif 2000 <= number < 4000:
                        ran = math.ceil((number - 2000) / 400)
                        return "Master " + str(ran)
                    elif 4000 <= number < 10000:
                        ran = math.ceil((number - 4000) / 1200)
                        return "Legend " + str(ran)
                    elif 10000 <= number < 20000:
                        ran = math.ceil((number - 10000) / 2000)
                        return "Grandmaster " + str(ran)

                for name in names:
                    nameind = names.index(name)
                    title = titles(lb[nameind])
                    out += str(name) + ": " + str(lb[nameind]) + " - " + title + "\n"
                out += "```"
                await ctx.send(out)
        else:
            if mode.lower() in duels:
                with open("registered.txt", "r") as players:
                    uuids = players.read().split()
                    for uuid in uuids:
                        duelstats = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}").json()["player"]["stats"]["Duels"]
                        solo = duelstats[f"{mode}_duel_wins"] if f"{mode}_duel_wins" in duelstats else 0
                        doubles = duelstats[f"{mode}_doubles_wins"] if f"{mode}_doubles_wins" in duelstats else 0
                        fours = duelstats[f"{mode}_four_wins"] if f"{mode}_four_wins" in duelstats else 0
                        if mode == "bridge":
                            bridge3 = duelstats[f"{mode}_3v3v3v3_wins"] if f"{mode}_3v3v3v3_wins" in duelstats else 0
                        else:
                            bridge3 = 0
                        lbduel = solo + doubles + fours + bridge3
                        leaderboard.append(lbduel)
                        templb.append(lbduel)
                        names.append(lbduel)
                    leaderboard.sort()
                    templb.sort()
                    for val in uuids:
                        temp = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={val}").json()["player"]
                        name = temp["displayname"]
                        solos = temp["stats"]["Duels"][f"{mode}_duel_wins"] if f"{mode}_duel_wins" in temp["stats"]["Duels"] else 0
                        solod = temp["stats"]["Duels"][f"{mode}_doubles_wins"] if f"{mode}_doubles_wins" in temp["stats"][
                            "Duels"] else 0
                        solof = temp["stats"]["Duels"][f"{mode}_four_wins"] if f"{mode}_four_wins" in temp["stats"][
                            "Duels"] else 0
                        if mode == "bridge":
                            b3 = temp["stats"]["Duels"][f"{mode}_3v3v3v3_wins"] if f"{mode}_3v3v3v3_wins" in temp["stats"][
                                "Duels"] else 0
                        else:
                            b3 = 0
                        quick = solos + solod + solof + b3
                        ind = templb.index(quick)
                        names[ind] = name
                        templb[ind] = -1
                players.close()
                lb = leaderboard[::-1]
                out = "```Leaderboard for " + mode + " wins\n"
                names = names[::-1]

                def rank(number):
                    if number < 50:
                        return "Not enough wins"
                    elif 50 <= number < 100:
                        ran = math.ceil((number - 50) / 10)
                        return "Rookie" + " " + str(ran)
                    elif 100 <= number < 250:
                        ran = math.ceil((number - 100) / 30)
                        return "Iron" + " " + str(ran)
                    elif 250 <= number < 500:
                        ran = math.ceil((number - 250) / 50)
                        return "Gold" + " " + str(ran)
                    elif 500 <= number < 1000:
                        ran = math.ceil((number - 500) / 100)
                        return "Diamond" + " " + str(ran)
                    elif 1000 <= number < 2000:
                        ran = math.ceil((number - 1000) / 200)
                        return "Master" + " " + str(ran)
                    elif 2000 <= number < 5000:
                        ran = math.ceil((number - 2000) / 600)
                        return "Legend" + " " + str(ran)
                    elif 5000 <= number < 10000:
                        ran = math.ceil((number - 5000) / 1000)
                        return "Grandmaster" + " " + str(ran)

                for name in names:
                    nameind = names.index(name)
                    title = rank(lb[nameind])
                    out += str(name) + ": " + str(lb[nameind]) + " - " + title + "\n"
                out += "```"
                await ctx.send(out)
            else:
                await ctx.send("Select an actual duel mode!")


@client.command(aliases=['q'])
async def queue(ctx):
    global songq
    global value
    await ctx.send(songq)
    await ctx.send(value)


@client.command()
async def loop(ctx):
    global looped
    if ctx.message.author.voice.channel == ctx.voice_client.channel:
        if looped is True:
            looped = False
            await ctx.send("No longer looping song")
        else:
            looped = True
            await ctx.send("Looping song!")
    else:
        await ctx.send("You must be in the bots vc to use this command!")


@client.command(aliases=["lq"])
async def loopqueue(ctx):
    global loopedqueue
    if ctx.message.author.voice.channel == ctx.voice_client.channel:
        if loopedqueue is True:
            loopedqueue = False
            await ctx.send("No longer looping queue")
        else:
            loopedqueue = True
            await ctx.send("Looping queue!")
    else:
        await ctx.send("You must be in the bots vc to use this command!")


@client.command(aliases=['p'])
async def play(ctx, *, search):
    global songq
    global value
    global botchannel
    global leave
    if botchannel is not None:
        botchannel = ctx.voice_client.channel
    channel = ctx.message.author.voice.channel
    if channel is None:
        await ctx.send("You must be in a vc to use this command!")
        return 0
    if channel == botchannel or botchannel is None:
        await duration()
        link = urllib.parse.urlencode({'search_query': search})
        content = urllib.request.urlopen('http://www.youtube.com/results?' + link)
        searchresult = re.findall(r'/watch\?v=(.{11})', content.read().decode())
        url = ('http://www.youtube.com/watch?v=' + searchresult[0])
        songq.append(url)
        if ctx.voice_client:
            await ctx.send("Added song!")
            if is_playing is False:
                _play(ctx)
        else:
            await channel.connect()
            leave = False
            botchannel = ctx.voice_client.channel
            _play(ctx)
    else:
        await ctx.send('Make sure to join the bots vc!')


async def duration():
    global is_playing
    is_playing = True
    await asyncio.sleep(2)
    is_playing = False


def _play(ctx):
    global is_playing
    is_playing = True
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        global value
        global songq
        info = ydl.extract_info(songq[value], download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda x: aftersong(ctx) if leave is False else print("Left vc"))


def aftersong(ctx):
    global value
    if looped is False:
        value += 1
    if loopedqueue is True and len(songq) == value:
        value = 0
    if value == len(songq) and looped is False and loopqueue is False:
        return 0
    else:
        _play(ctx)


@client.command(aliases=['s'])
async def skip(ctx):
    if ctx.message.author.voice.channel == ctx.voice_client.channel:
        if ctx.voice_client:
            vc = ctx.author.voice.channel
            global leave
            leave = False
            ctx.voice_client.stop()
            global value
            global songq
            if value < len(songq):
                _play(vc)
                await ctx.send("Skipping!")
            else:
                value -= value
                songq.clear()
    else:
        await ctx.send("Make sure you are in the bots vc!")


@client.command(aliases=['dc'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    global botchannel
    botchannel = ctx.voice_client.channel
    global songq
    global value
    global is_playing
    global looped
    global loopedqueue
    global leave
    if channel == botchannel:
        is_playing = False
        if ctx.voice_client:
            leave = True
            await ctx.voice_client.disconnect()
            songq.clear()
            botchannel = None
            looped = False
            loopedqueue = False
            if value > 0:
                value = value - value
        else:
            await ctx.send("I am not in vc right now!")
            songq.clear()
            looped = False
            loopedqueue = False
            value = 0
        leave = False
    else:
        await ctx.send("You are not in the bots vc!")


@client.command(aliases=['reset'])
async def musicreset(ctx):
    if ctx.message.author.id == 335958694585958400 or ctx.message.author.id == 258048636653535234:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        global songq
        global value
        global looped
        global botchannel
        global is_playing
        global looped
        global loopedqueue
        songq.clear()
        looped = False
        is_playing = False
        botchannel = None
        looped = False
        loopedqueue = False
        value = 0
    else:
        await ctx.send("You do not have perms to run this command!")


@client.command(aliases=["np"])
async def nowplaying(ctx):
    await ctx.send(songq[value])


@client.command()
async def test(ctx):
    await ctx.send("testing")


@client.event
async def on_message(msg):
    msg.content = msg.content.lower()
    if msg.content.count('your mom') > 0 or msg.content.count('ur mom') > 0:
        if msg.author.id == 471313677618774031:
            with open("lureenurmom.txt", "r") as urmom:
                contents = int(urmom.read())
                contents = contents + 1
                await msg.channel.send("Lauren has made " + str(contents) + " horrible your mom jokes. Tell her to stop")
                urmom.close()
                with open("lureenurmom.txt", "w") as newurmom:
                    newurmom.write(str(contents))
                    newurmom.close()
        if msg.author.id != 876160756763226113 and msg.author.id != 471313677618774031:
            await msg.channel.send("Do not speak of her in such a way")
    elif msg.content == 'sorry':
        if msg.author.id != 876160756763226113:
            await msg.channel.send("mommy")
    elif msg.content == "mommy":
        if msg.author.id != 876160756763226113:
            await msg.channel.send("sorry")
    await client.process_commands(msg)


@client.command()
async def hangman(ctx, member: discord.Member):
    global blank
    global gameon
    global __hangman
    global blankarr
    if gameon is True:
        await ctx.send("A game is already active")
        return
    else:
        player1 = ctx.author
        player2 = member
        duelmsg = await ctx.send(player2.mention + ", " + player1.mention + ", challenged you to hangman!")
        await duelmsg.add_reaction("✅")

        def check1(reaction, user):
            return user == player2 and str(reaction.emoji) == "✅"

        def check2(m):
            return m.author == player1 and m.channel == channel

        try:
            await client.wait_for('reaction_add', timeout=20, check=check1)
            gameon = True
            dm = await player1.send("What do you want your word to be?")
            channel = dm.channel
            try:
                word = await client.wait_for("message", timeout=20, check=check2)
                _hangman = word.content.lower()
                __hangman = list(_hangman)
                blankarr = []
                print(__hangman)
                for val in __hangman:
                    if val != " ":
                        blank = blank + "- "
                        blankarr.append("- ")
                    else:
                        blank = blank + "   "
                        blankarr.append("   ")
                await ctx.send(player2.mention + ", the game has begun, your word to guess is:")
                await ctx.send(blank)

                async def guesses():
                    global gameon
                    global active
                    global lives
                    global blank
                    global guessed
                    global guessedarr
                    global _guess
                    global __hangman
                    global blankarr
                    active = True

                    def guesscheck(e):
                        return e.author == player2 and e.channel == ctx.channel

                    while active is True:
                        try:
                            letter = await client.wait_for("message", check=guesscheck)
                            _guess = letter.content.lower()
                            if _guess == _hangman:
                                await ctx.send(player2.mention + " HAS WON THE GAME!")
                                blank = ""
                                blankarr.clear()
                                __hangman.clear()
                                _guess = ""
                                lives = 0
                                guessed = ""
                                guessedarr.clear()
                                active = False
                                gameon = False
                            elif len(_guess) > 1:
                                await ctx.send("Your guess can't be more than 1 character!")
                            else:
                                if _guess in guessedarr:
                                    await ctx.send("You already guessed that dummy!")
                                else:
                                    guessed = guessed + _guess + " "
                                    guessedarr.append(_guess)
                                    if _guess not in __hangman:
                                        lives = lives + 1
                                        if lives == 1:
                                            await ctx.send(file=discord.File("head.png"))
                                        elif lives == 2:
                                            await ctx.send(file=discord.File("body.png"))
                                        elif lives == 3:
                                            await ctx.send(file=discord.File("l-arm.png"))
                                        elif lives == 4:
                                            await ctx.send(file=discord.File("r-arm.png"))
                                        elif lives == 5:
                                            await ctx.send(file=discord.File("l-leg.png"))
                                        elif lives == 6:
                                            await ctx.send(file=discord.File("end.png"))
                                            await ctx.send(player2.mention + ", you lost! The word was: " + _hangman)
                                            blank = ""
                                            blankarr.clear()
                                            __hangman.clear()
                                            _guess = ""
                                            active = False
                                            lives = 0
                                            guessed = ""
                                            guessedarr.clear()
                                            gameon = False
                                            return 0
                                    else:
                                        for char in __hangman:
                                            if _guess == char:
                                                ind = __hangman.index(char)
                                                __hangman[ind] = "done"
                                                blankarr[ind] = char + " "
                                            blank = ""
                                            for x in blankarr:
                                                blank = blank + x
                                    await ctx.send(blank)
                                    await ctx.send(guessed)
                                    if "- " not in blankarr:
                                        active = False
                                        await ctx.send(player2.mention + ". YOU WON!")
                                        blank = ""
                                        _guess = ""
                                        blankarr.clear()
                                        __hangman.clear()
                                        guessedarr.clear()
                                        lives = 0
                                        guessed = ""
                                        gameon = False
                        except asyncio.TimeoutError:
                            return

                await guesses()

            except asyncio.TimeoutError:
                await ctx.send(player1.mention + " took too long! What a loser.")
                gameon = False
        except asyncio.TimeoutError:
            await ctx.send("Out of time!")


@client.command()
async def endgame(ctx):
    global blank, _guess, blankarr, __hangman, guessedarr, lives, guessed, gameon, active
    if ctx.author.id == 335958694585958400:
        blank = ""
        _guess = ""
        blankarr.clear()
        __hangman.clear()
        guessedarr.clear()
        lives = 0
        guessed = ""
        gameon = False
        active = False
    else:
        await ctx.send("You don't have permission to run this command")


@client.command()
async def duel(ctx, member: discord.Member):
    global active
    if active is True:
        await ctx.send("A duel is ongoing!")
    else:
        player1 = ctx.author
        player2 = member
        if player2.id == 876160756763226113:
            await ctx.send("Nice try loser")
            return
        channel = ctx.channel
        dmsg = await ctx.send(player1.mention + " HAS CHALLENGED" + player2.mention + " TO A DUEL TO THE DEATH!")
        await dmsg.add_reaction("✅")

        def maincheck(reaction, user):
            return user == player2 and str(reaction.emoji) == "✅"

        try:
            await client.wait_for("reaction_add", timeout=30, check=maincheck)
        except asyncio.TimeoutError:
            await ctx.send(player2.mention + " WAS TOO SCARED!")
        else:
            await ctx.send("THE DUEL IS COMMENCING. CHECK YOUR DMS TO PICK YOUR ATTACKS!")
            dmone = await player1.send("What element do you want to use?\n Acceptable elements are 'water, fire, earth, and air'")
            channel1 = dmone.channel

            def checkone(o):
                return o.author == player1 and o.channel == channel1

            try:
                att1 = await client.wait_for("message", timeout=30, check=checkone)
                style1 = att1.content.lower()
                dmtwo = await player2.send("What element do you want to use?\n Acceptable elements are 'water, fire, earth, and air'")
                channel2 = dmtwo.channel

                def checktwo(t):
                    return t.author == player2 and t.channel == channel2

                try:
                    att2 = await client.wait_for("message", timeout=30, check=checktwo)
                    style2 = att2.content.lower()
                    active = True

                    async def battle():
                        global turn, lives1, lives2, burn1, burn2, sleep1, sleep2, freeze2, freeze1, earth1, earth2, active
                        lives1 = 200
                        lives2 = 200
                        if style1 not in styles or style2 not in styles:
                            await ctx.send("Someone picked a style that isn't an option! Reduel and try again!")
                            active = False
                            return
                        else:
                            await ctx.send(
                                player1.mention + " picked " + style1 + " and " + player2.mention + " picked " + style2)

                            def _checkone(p):
                                return p.author == player1 and p.content.lower() == "attack" and p.channel == channel

                            def _checktwo(r):
                                return r.author == player2 and r.content.lower() == "attack" and r.channel == channel

                            while lives1 > 0 and lives2 > 0:
                                if turn == 0:
                                    try:
                                        await client.wait_for("message", check=_checkone)
                                        if sleep1 is True:
                                            if randint(0, 2) != 2:
                                                await ctx.send("Zzz...")
                                                turn = 1
                                            else:
                                                await ctx.send("Sleep has dissipated.")
                                                sleep1 = False
                                                turn = 1
                                        else:
                                            if freeze1 is True:
                                                if randint(0, 1) != 1:
                                                    await ctx.send("Brrr...")
                                                    turn = 1
                                                else:
                                                    await ctx.send("The ice has melted.")
                                                    freeze1 = False
                                                    turn = 1
                                            else:
                                                atck1 = randint(0, 2)
                                                if style1 == "fire":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 1
                                                    else:
                                                        if atck1 == 0:
                                                            await ctx.send(
                                                                "You used burn on the enemy! They will now slowly take damage each turn.")
                                                            burn2 = True
                                                            turn = 1
                                                        elif atck1 == 1:
                                                            dmg = randint(5, 65)
                                                            lives2 -= dmg
                                                            await ctx.send(
                                                                "You used fire tornado and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                        elif atck1 == 2:
                                                            dmg = randint(30, 40)
                                                            lives2 -= dmg
                                                            await ctx.send(
                                                                "You used heatwave and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                elif style1 == "water":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 1
                                                    else:
                                                        if atck1 == 0:
                                                            freeze2 = True
                                                            await ctx.send("You used freeze on the opponent!")
                                                            turn = 1
                                                        elif atck1 == 1:
                                                            dmg = randint(20, 50)
                                                            lives2 -= dmg
                                                            await ctx.send(
                                                                "You used power hose and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                        elif atck1 == 2:
                                                            dmg = randint(0, 35)
                                                            lives2 -= dmg
                                                            await ctx.send("You used splash and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                elif style1 == "air":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 1
                                                    else:
                                                        if atck1 == 0:
                                                            sleep2 = True
                                                            await ctx.send("You used sleep on the opponent!")
                                                            turn = 1
                                                        elif atck1 == 1:
                                                            dmg = randint(50, 70)
                                                            lives2 -= dmg
                                                            await ctx.send("You used debris and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                        elif atck1 == 2:
                                                            dmg = randint(0, 10)
                                                            lives2 += dmg
                                                            await ctx.send(
                                                                "You used breeze! Your opponent enjoyed it so much they recovered " + str(dmg) + " health.")
                                                            turn = 1
                                                elif style1 == "earth":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 1
                                                    else:
                                                        if atck1 == 0:
                                                            earth1 += 10
                                                            await ctx.send(
                                                                "You used the earth to increase your damage by 10!")
                                                            turn = 1
                                                        elif atck1 == 1:
                                                            dmg = randint(40, 50) + earth1
                                                            lives2 -= dmg
                                                            await ctx.send("You used boulder and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                        elif atck1 == 2:
                                                            dmg = randint(40, 50) + earth1
                                                            lives2 -= dmg
                                                            await ctx.send(
                                                                "You used avalanche and dealt " + str(dmg) + " damage!")
                                                            turn = 1
                                                if burn1 is False:
                                                    await ctx.send("Player 2's turn\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                else:
                                                    if randint(0, 5) != 5:
                                                        dmg = randint(5, 10)
                                                        lives1 -= dmg
                                                        await ctx.send("You lost " + str(dmg) + " health to burning.\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                    else:
                                                        await ctx.send("Burning wore off.\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                        burn1 = False
                                    except asyncio.TimeoutError:
                                        return
                                elif turn == 1:
                                    try:
                                        await client.wait_for("message", check=_checktwo)
                                        if sleep2 is True:
                                            if randint(0, 2) != 2:
                                                await ctx.send("Zzz...")
                                                turn = 0
                                            else:
                                                await ctx.send("Sleep has dissipated.")
                                                sleep2 = False
                                                turn = 0
                                        else:
                                            if freeze2 is True:
                                                if randint(0, 1) != 1:
                                                    await ctx.send("Brrr...")
                                                    turn = 0
                                                else:
                                                    await ctx.send("The ice has melted.")
                                                    freeze2 = False
                                                    turn = 0
                                            else:
                                                atck2 = randint(0, 2)
                                                if style2 == "fire":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 0
                                                    else:
                                                        if atck2 == 0:
                                                            await ctx.send(
                                                                "You used burn on the enemy! They will now slowly take damage each turn.")
                                                            burn1 = True
                                                            turn = 0
                                                        elif atck2 == 1:
                                                            dmg = randint(5, 75)
                                                            lives1 -= dmg
                                                            await ctx.send(
                                                                "You used fire tornado and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                        elif atck2 == 2:
                                                            dmg = randint(30, 40)
                                                            lives1 -= dmg
                                                            await ctx.send(
                                                                "You used heatwave and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                elif style2 == "water":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 0
                                                    else:
                                                        if atck2 == 0:
                                                            freeze1 = True
                                                            await ctx.send("You used freeze on the opponent!")
                                                            turn = 0
                                                        elif atck2 == 1:
                                                            dmg = randint(20, 50)
                                                            lives1 -= dmg
                                                            await ctx.send(
                                                                "You used power hose and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                        elif atck2 == 2:
                                                            dmg = randint(0, 35)
                                                            lives1 -= dmg
                                                            await ctx.send("You used splash and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                elif style2 == "air":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 0
                                                    else:
                                                        if atck2 == 0:
                                                            sleep1 = True
                                                            await ctx.send("You used sleep on the opponent!")
                                                            turn = 0
                                                        elif atck2 == 1:
                                                            dmg = randint(50, 70)
                                                            lives1 -= dmg
                                                            await ctx.send("You used debris and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                        elif atck2 == 2:
                                                            dmg = randint(0, 10)
                                                            lives1 += dmg
                                                            await ctx.send(
                                                                "You used breeze! Your opponent enjoyed it so much they recovered " + str(dmg) + " health.")
                                                            turn = 0
                                                elif style2 == "earth":
                                                    if randint(0, 5) == 5:
                                                        await ctx.send("Your attack missed!")
                                                        turn = 0
                                                    else:
                                                        if atck2 == 0:
                                                            earth2 += 10
                                                            await ctx.send(
                                                                "You used the earth to increase your damage by 10!")
                                                            turn = 0
                                                        elif atck2 == 1:
                                                            dmg = randint(40, 50) + earth1
                                                            lives1 -= dmg
                                                            await ctx.send("You used boulder and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                        elif atck2 == 2:
                                                            dmg = randint(40, 50) + earth1
                                                            lives1 -= dmg
                                                            await ctx.send(
                                                                "You used avalanche and dealt " + str(dmg) + " damage!")
                                                            turn = 0
                                                if burn2 is False:
                                                    await ctx.send("Player 1's turn\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                else:
                                                    if randint(0, 5) != 5:
                                                        dmg = randint(5, 10)
                                                        lives2 -= dmg
                                                        await ctx.send("You lost " + str(dmg) + " health to burning.\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                    else:
                                                        await ctx.send("Burning wore off.\n" + player1.mention + " has " + str(lives1) + "\n" + player2.mention + " has " + str(lives2))
                                                        burn2 = False
                                    except asyncio.TimeoutError:
                                        return
                                if lives1 <= 0 and lives2 <= 0:
                                    await ctx.send(player1.mention + " and " + player2.mention + " tied this duel! Lame.")
                                    freeze2 = False
                                    freeze1 = False
                                    sleep1 = False
                                    sleep2 = False
                                    burn1 = False
                                    burn2 = False
                                    earth1 = 0
                                    earth2 = 0
                                    turn = 0
                                    active = False
                                elif lives1 <= 0:
                                    await ctx.send(player2.mention + " HAS TRIUMPHED IN THE DUEL!")
                                    freeze2 = False
                                    freeze1 = False
                                    sleep1 = False
                                    sleep2 = False
                                    burn1 = False
                                    burn2 = False
                                    earth1 = 0
                                    earth2 = 0
                                    turn = 0
                                    active = False
                                elif lives2 <= 0:
                                    await ctx.send(player1.mention + " HAS TRIUMPHED IN THE DUEL!")
                                    freeze2 = False
                                    freeze1 = False
                                    sleep1 = False
                                    sleep2 = False
                                    burn1 = False
                                    burn2 = False
                                    earth1 = 0
                                    earth2 = 0
                                    turn = 0
                                    active = False

                    await battle()

                except asyncio.TimeoutError:
                    await ctx.send(player2.mention + " TOOK TOO LONG! WHAT A LOSER!")
                    return
            except asyncio.TimeoutError:
                await ctx.send(player1.mention + " TOOK TOO LONG! WHAT A LOSER!")
                return


@client.command(aliases=["l"])
async def lyrics(ctx, *, artist):
    alist = list(artist.lower())
    for let in alist:
        ind = alist.index(let)
        if let == " " or let == "/":
            del alist[ind]
    curart = ""
    for val in alist:
        curart = curart + val

    def check(e):
        return e.author == ctx.author

    await ctx.send("What is the song name")
    try:
        msg = await client.wait_for("message", timeout=30, check=check)
        song = msg.content.lower()
        slist = list(song)
        for lets in slist:
            inds = slist.index(lets)
            if lets == " " or lets  == "/":
                del slist[inds]
        cursong = ""
        for vals in slist:
            cursong = cursong + vals
        try:
            content = requests.get("https://www.azlyrics.com/lyrics/" + curart + "/" + cursong + ".html").text
            try:
                soup = bs4.BeautifulSoup(content, "html.parser")
                lyrics = soup.find("div", {"class": None, "id": None}).text
                await ctx.send(lyrics)
            except discord.errors.HTTPException:
                await ctx.send("https://www.azlyrics.com/lyrics/" + curart + "/" + cursong)
        except AttributeError:
            await ctx.send("The page either doesn't exist or you had a typo")
    except asyncio.TimeoutError:
        await ctx.send("You took too long")


client.run(token)
