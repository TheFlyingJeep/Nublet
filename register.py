import requests


async def addregister(ctx, user):
    try:
        player = requests.get("https://api.mojang.com/users/profiles/minesraft/" + user)
        player = player.json()
        uuid = player["id"]
        with open("registered.txt", "r") as rr:
            people = rr.read().split()
            if uuid in people:
                await ctx.send("This user is already registered")
            else:
                with open("registered.txt", "a") as rfile:
                    rfile.write(uuid + "\n")
                    await ctx.send("User added")
    except ValueError:
        await ctx.send("Couldn't find a uuid for this user")
        return


async def getusers(ctx):
    out = "```"
    with open("registered.txt", "r") as users:
        people = users.read().split()
        for val in people:
            out += val + "\n"
    out += "```"
    await ctx.send(out)