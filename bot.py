import discord
from discord.ext import commands
import Hangman as Hms
import register as r
import dueldatagetter as ddg
import music as p
import math
import valorant
from discord.utils import get

client = commands.Bot(command_prefix=".")
with open("token.txt", "r") as t:
    token = t.read()
#key = "RGAPI-d0ff9d74-b952-432b-a1fb-8d98686c257d"
#CLIENT = valorant.AsyncClient(key)


#@client.command()
#async def getdata(ctx, username):
#    person = await CLIENT.get_user_by_name(username)
#    print(person)


@client.event
async def on_ready():
    print("Nublet is running")


@client.event
async def on_message(message):
    if message.author.id == 720288689141579776 and (message.content.lower().count("your mom") > 0 or message.content.lower().count("ur mom") > 0):
        with open("grassurmom.txt", "r") as gmom:
            count = gmom.read()
        with open("grassurmom.txt", "w") as gmom2:
            gmom2.write(str(int(count) + 1))
        await message.channel.send("Grass has now made " + count + " HORRIBLE your mom jokes. REFRAIN SMH >:(")
    elif message.author.id == 471313677618774031 and (message.content.lower().count("your mom") > 0 or message.content.lower().count("ur mom") > 0):
        with open("lureenyourmom.txt", "r") as lmom:
            count = lmom.read()
        with open("lureenyourmom.txt", "w") as lmom2:
            lmom2.write(str(int(count) + 1))
        await message.channel.send("Lauren has now made " + count + " HORRIBLE your mom jokes. TELL HER TO STOP")
    elif message.content == "mommy" and message.author != client.user:
        await message.channel.send("sorry")
    elif message.content == "sorry" and message.author != client.user:
        await message.channel.send("mommy")
    await client.process_commands(message)


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if client.user.id == member.id and before.channel is not None and after.channel is None:
        if before.channel.guild.id in p.servers:
            await p.servers[before.channel.guild.id].messagechannel.send("I'll leave you alone I guess 🙄")
            del p.servers[before.channel.guild.id]


@client.command()
async def hangman(ctx, player2: discord.Member):
    if player2.id in Hms.games:
        await ctx.send("That user is already playing a game!")
    else:
        await Hms.startgame(client, ctx, player2)


@client.command()
async def guess(ctx):
    if ctx.author.id not in Hms.games:
        await ctx.send("You are not playing a game rn")
        return
    try:
        guess = ctx.message.content.split()[1]
        await Hms.runguess(ctx, guess.lower())
    except IndexError:
        await ctx.send("Put an actual guess")


@client.command()
async def register(ctx):
    try:
        user = ctx.message.content.split()[1]
        await r.addregister(ctx, user.lower())
    except IndexError:
        await ctx.send("Put an ign")


@client.command()
async def registered(ctx):
    await r.getusers(ctx)


@client.command(aliases=["duelslb", "dlb"])
async def duelsleaderboard(ctx):
    modes = ["sumo", "sw", "bridge", "bow", "op", "combo", "bowspleef"]
    try:
        mode = ctx.message.content.split()[1]
        if mode.lower() in modes:
            await ddg.modelb(ctx, mode.lower())
        else:
            await ctx.send("Provide an actual mode")
    except IndexError:
        await ddg.overalllb(ctx)


@client.command(aliases=["p", "add"])
async def play(ctx, *, song):
    try:
        vc = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("You must be in a vc")
        return
    if ctx.guild.id not in p.servers:
        p.servers[ctx.guild.id] = p.BotServers(ctx.guild)
        obj = p.servers[ctx.guild.id]
        obj.messagechannel = ctx.channel
        await vc.connect()
        obj.vc_channel = vc
        await p.get_song(obj, ctx, client, song)
    else:
        obj = p.servers[ctx.guild.id]
        if obj.vc_channel != vc:
            await ctx.send("You must be in the bots vc!")
            return
        await p.get_song(obj, ctx, client, song)


@client.command(aliases=["dc"])
async def leave(ctx):
    if ctx.guild.id in p.servers:
        bot = p.servers[ctx.guild.id]
        if bot.vc_channel != ctx.author.voice.channel:
            await ctx.send("You are not in my vc!")
        else:
            await ctx.voice_client.disconnect()


@client.command(aliases=["s", "next", "n"])
async def skip(ctx):
    try:
        vc = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("You aren't even IN a vc you loser")
        return
    if ctx.guild.id in p.servers:
        bot = p.servers[ctx.guild.id]
        if vc == bot.vc_channel:
            ctx.voice_client.stop()
            await ctx.send("Skipping")
        else:
            await ctx.send("You are not in the bots vc")
    else:
        await ctx.send("I'm not in a vc rn :P")


@client.command(aliases=["q"])
async def queue(ctx):
    if ctx.guild.id in p.servers:
        obj = p.servers[ctx.guild.id]
        try:
            temp = ctx.message.content.split()[1]
            try:
                page = int(temp)
                if page <= 0 or (page - 1) * 10 > len(obj.queue):
                    await ctx.send("Your number must be in range of the queue")
                    return
                out = "```"
                for num in range(math.floor(page - 1) * 10, ((math.floor(page - 1)) + 1) * 10):
                    try:
                        temp = obj.queue[num]
                        if num == obj.curnum:
                            out += "<Now playing> "
                        seconds = obj.queue[num - 1]["duration"] % 60
                        secondsstr = "0" + str(seconds) if seconds < 10 else str(seconds)
                        out += str(num + 1) + ": " + obj.queue[num - 1]["title"] + " " + str(round(obj.queue[num - 1]["duration"] / 60)) + ":" + secondsstr + "\n"
                    except IndexError:
                        break
                out += "Currently on song " + str(obj.curnum + 1) + "\n"
                out += "Looping song: " + str(obj.is_looping) + ". " + "Looping queue: " + str(obj.is_looping_queue) + "```"
                await ctx.send(out)
            except ValueError:
                await ctx.send("Give a NUMBER as an input (ex: .q 2)")
        except IndexError:
            out = "```"
            for num in range(math.floor(obj.curnum/10) * 10, ((math.floor(obj.curnum/10)) + 1) * 10):
                try:
                    temp = obj.queue[num]
                    if num == obj.curnum:
                        out += "<Now playing> "
                    seconds = obj.queue[num - 1]["duration"] % 60
                    secondsstr = "0" + str(seconds) if seconds < 10 else str(seconds)
                    out += str(num + 1) + ": " + obj.queue[num - 1]["title"] + " " +  str(round(obj.queue[num - 1]["duration"] / 60)) + ":" + secondsstr + "\n"
                except IndexError:
                    break
            out += "Currently on song " + str(obj.curnum + 1) + "\n"
            out += "Looping song: " + str(obj.is_looping) + ". " + "Looping queue: " + str(obj.is_looping_queue) + "```"
            await ctx.send(out)
    else:
        await ctx.send("I'm not in a vc rn :P")


@client.command(aliases=["lq"])
async def loopqueue(ctx):
    try:
        vc = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("You aren't even IN a vc you loser")
        return
    if ctx.guild.id in p.servers:
        bot = p.servers[ctx.guild.id]
        if vc == bot.vc_channel:
            if bot.is_looping_queue:
                bot.is_looping_queue = False
                await ctx.send("No longer looping queue!")
            else:
                bot.is_looping_queue = True
                await ctx.send("Now looping queue")
        else:
            await ctx.send("You are not in the bots vc")
    else:
        await ctx.send("I'm not in a vc rn :P")


@client.command(aliases=["lp"])
async def loop(ctx):
    try:
        vc = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("You aren't even IN a vc you loser")
        return
    if ctx.guild.id in p.servers:
        bot = p.servers[ctx.guild.id]
        if vc == bot.vc_channel:
            if bot.is_looping:
                bot.is_looping = False
                await ctx.send("No longer looping this song!")
            else:
                bot.is_looping = True
                await ctx.send("Now looping this song!")
        else:
            await ctx.send("You are not in the bots vc")
    else:
        await ctx.send("I'm not in a vc rn :P")


@client.command(aliases=["l"])
async def lyrics(ctx):
    if ctx.guild.id in p.servers:
        obj = p.servers[ctx.guild.id]
        if ctx.author.voice.channel != obj.vc_channel:
            await ctx.send("You aren't even IN my vc >:(")
            return
        else:
            await p.get_lyrics(ctx, obj)
    else:
        await ctx.send("I am not in vc")


@client.command()
async def download(ctx, *, song):
    if ctx.author.id != 335958694585958400:
        await ctx.send("You can't run this command! >:(")
    else:
        await p.downloader(ctx, song)


@client.command(aliases=["np"])
async def nowplaying(ctx):
    if ctx.guild.id in p.servers:
        await ctx.send(p.servers[ctx.guild.id].url[p.servers[ctx.guild.id].curnum])
    else:
        await ctx.send("I'm not in vc rn")


client.run(token)