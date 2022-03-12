import requests
import statsdict as sd


async def modelb(ctx, mode):
    with open("registered.txt", "r") as r:
        users = r.read().split()
        output = "```"
        values = []
        igns = []
        for val in users:
            data = await sd.getstat(api, mode)



async def overalllb(ctx):
    await ctx.send("Developing")