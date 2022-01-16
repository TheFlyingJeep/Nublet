import requests
import statsdict as sd
with open("api_key.txt", "r") as apik:
    api_key = apik.read()


async def modelb(ctx, mode):
    with open("registered.txt", "r") as r:
        users = r.read().split()
        for val in users:
            api = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={val}").json()["player"]
            data = await sd.getstat(api, mode)
            print(data)


async def overalllb(ctx):
    await ctx.send("Developing")