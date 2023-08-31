import discord, json
import activity as act
from discord.ext import commands
import trivia as triv
import vroomskirt as vs
from multiprocessing import Process
import connections as c

inte = discord.Intents.all()
inte.members = True
bot = commands.Bot(command_prefix=">", intents=inte)

@bot.event
async def on_ready():
    print("Tennis ball online")

@bot.event
async def on_raw_reaction_add(payload):
    if not payload.member.bot  and str(payload.emoji) == "✅" and payload.message_id in triv.trivia_games:
        await triv.try_join(payload)
    elif not payload.member.bot  and str(payload.emoji) == "✅" and payload.message_id in vs.vsgames:
        await vs.tryJoin(payload)
    elif not payload.member.bot and str(payload.emoji) == "⏩" and payload.message_id in triv.trivia_games:
        await triv.try_start(payload)
    
@bot.command(name="activity")
async def activity(ctx):
    await act.listAllPlayerActivity(ctx, bot)
    
@bot.command(name="register", aliases=["reg"])
async def register(ctx):
    await act._register(ctx)
    
@bot.command(name="unregister", aliases=["unreg"])
async def unregister(ctx):
    await act._unregister(ctx)

@bot.command(name="trivia")
async def trivia(ctx):
    await triv.prompt_players(ctx, bot)

@bot.command(name="vroomskirt", aliases=["vs"])
async def vroomskirt(ctx):
    await vs.startGame(ctx, bot)
        
if __name__ == "__main__":
    with open("secrets.json") as sec:
        proc = Process(target=c.make_server, args=())
        proc.start()
        data = json.load(sec)
        bot.run(data["token"])
        proc.join()