import discord, json
from discord import CustomActivity
        
async def getUsers():
    with open("players.txt", "r") as plays:
        data = plays.read()
        return data.split()
        
async def _register(ctx):
    user = ctx.author
    data = await getUsers()
    if str(user.id) in data:
        await ctx.send("User already registered")
    else:
        data.append(str(user.id))
        with open("players.txt", "w") as play:
            for i in data:
                play.write(i + "\n")
        await ctx.send("Registered")
        
async def _unregister(ctx):
    user = ctx.author
    data = await getUsers()
    if str(user.id) not in data:
        await ctx.send("User not registered")
    else:
        data.remove(str(user.id))
        with open("players.txt", "w") as play:
            for i in data:
                play.write(i + "\n")
        await ctx.send("Unregistered")
        
async def listAllPlayerActivity(ctx, bot):
    data = await getUsers()
    embed = discord.Embed(title="What everyone doing?")
    for user in ctx.guild.members:
        if (str(user.id) in data):
            gameStr = f""
            colorStr = ""
            sta = str(user.desktop_status)
            colorStr = ":black_circle: " if sta == "offline" else ":red_circle: " if sta == "dnd" else ":yellow_circle: " if sta == "idle" else ":green_circle: "
            for activity in user.activities:
                if not isinstance(activity, CustomActivity):
                                if hasattr(activity, "artist"):
                                    gameStr += f":musical_note: Listening to {activity.title} by {activity.artist}\n"
                                else:
                                    gameStr += f":video_game: Playing {activity.name}\n"
            embed.add_field(name=colorStr + " " + user.name,value=gameStr if gameStr != "" else "Not doing anything", inline=False)
            embed.add_field(name="",value="", inline=False)
    embed.add_field(name="Don't see yourself?", value="Add yourself with the >register command!", inline=False)
    embed.add_field(name="Want to remove yourself?", value="Use the >unregister command!")
    await ctx.send(embed=embed)