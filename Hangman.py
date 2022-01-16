import asyncio
import discord


class HangmanGames:
    def __int__(self):
        self.phrase = None
        self.phrasearr = []
        self.blankarr = []
        self.lives = None
        self.guessed = None


games = {}


async def startgame(client, ctx, player2):
    dmsg = await ctx.send(ctx.author.mention + " has challenged " + player2.mention + " to a hangman duel!")
    await dmsg.add_reaction("✅")

    def hmancheck(reaction, user):
        return user == player2 and str(reaction.emoji) == "✅"

    def getmsg(p):
        return p.author == ctx.author and p.channel == askmsg.channel

    try:
        await client.wait_for("reaction_add", timeout=30, check=hmancheck)
        askmsg = await ctx.author.send("What do you want your phrase to be?")

        try:
            msg = await client.wait_for("message", timeout=45, check=getmsg)
            games[player2.id] = HangmanGames()
            games[player2.id].lives = 0
            games[player2.id].guessed = []
            games[player2.id].phrase = msg.content.lower()
            temparr = list(msg.content.lower())
            games[player2.id].phrasearr = temparr
            blank = []
            for val in temparr:
                if val == " ":
                    blank.append(" ")
                else:
                    blank.append("-")
            games[player2.id].blankarr = blank
            await ctx.send("The message is:  " + joinblank(games[player2.id].blankarr))

        except asyncio.TimeoutError:
            await ctx.send(ctx.author.mention + " took too long coming up with a phrase!")

    except asyncio.TimeoutError:
        await ctx.send(player2.mention + " took too long")


async def runguess(ctx, guess):
    game = games[ctx.author.id]
    if guess in game.guessed:
        await ctx.send("You already guessed that dummy!")
        return
    if guess == game.phrase:
        await winner(ctx)
        return
    elif len(guess) > 1:
        await ctx.send("Invalid guess")
        return
    else:
        game.guessed.append(guess)
        if guess in game.phrasearr:
            for i, val in enumerate(game.phrasearr):
                if guess == val:
                    game.blankarr[i] = guess
            await ctx.send(joinblank(game.blankarr))
            if game.blankarr == game.phrasearr:
                await winner(ctx)
                return
        else:
            game.lives += 1
            await ctx.send("You have lost a life. Lives remaining are: " + str(6 - game.lives))
            await ctx.send(file=discord.File(f"draw{game.lives}.png"))
            if game.lives == 6:
                await loser(ctx)
                return
    await ctx.send("Letters guessed are: " + joinblank(game.guessed))


async def winner(ctx):
    await ctx.send("You won! Good job")
    del games[ctx.author.id]


async def loser(ctx):
    await ctx.send("You lost! The phrase was: " + games[ctx.author.id].phrase)
    del games[ctx.author.id]


def joinblank(word):#spaces screwing me over and im too lazy to make a better fix
    out = ""
    for val in word:
        if val == " ":
            out += "   "
        else:
            out += val + " "
    return out
