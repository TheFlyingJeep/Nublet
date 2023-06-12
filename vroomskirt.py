import asyncio, discord, time
vsgames = {}

class VroomSkirt:
    def __init__(self, ctx, msg, client) -> None:
        self.ctx = ctx
        self.msg = msg
        self.client = client
        self.started = False
        self.players = [ctx.author]
        self.alive = [True]
        self.turn = 0
        self.right = None
        self.channel = None
        self.vroommessage = None
        self.deathmessage = None
        self.brakecount = 0
        self.brake = False
        self.braked = []

    async def initGame(self):
        for i in range(1,10):
            time.sleep(1)
            await self.msg.edit(content=f"{self.ctx.author.mention} is starting a game of vroomskirt! You have {10-i} seconds to join by reacting here!")
        if len(self.players) > 1:
            await self.msg.edit(content="This game has already started. You can start a new one with >vroomskirt!")
            self.started = True
            self.channel = await self.msg.guild.create_text_channel(f"Vroomskirt-{self.msg.id}")
            st = ""
            for i in self.players:
                st += i.mention + " "
            await self.channel.send(st)
            loop = asyncio.get_event_loop()
            gameTask = loop.create_task(gameLoop(self))
            await gameTask
        else:
            await self.msg.edit(content="There are not enough players to start this game")
            del vsgames[self.msg.id]

    async def updateTurn(self):
        await self.increment()
        while not self.alive[self.turn]:
            await self.increment()

    async def increment(self):
        if self.right is None or self.right is True:
            self.turn += 1
            if (self.turn >= len(self.players)):
                self.turn = 0
        else:
            self.turn -= 1
            if self.turn < 0:
                self.turn = len(self.players)-1

    async def generateMsg(self):
        st = "Vroomskirt game: \n"
        if self.right is not None:
            st += "The current direction is "
            st += "RIGHT\n" if self.right else "LEFT\n" 
        st += "It is currently " + self.players[self.turn].mention + "'s turn!\n"
        for i, v in enumerate(self.players):
            st += v.name + " - " 
            st += "ALIVE" if self.alive[i] else "DEAD"
            if i == self.turn:
                st += " - CURRENT TURN"
            st += "\n"
        return st

async def startGame(ctx, bot):
    embed = discord.Embed(title="Vroomskirt rules: ")
    embed.add_field(name="Use the arrows given to move the direction of the game.", value="You can either keep the game moving in the same direction or reverse the direction.", inline=False)
    embed.add_field(name="The two emojis with one arrow represent vrooming. A vroom must go in the same direction as the current direction.", value="In terms of direction, going down the list means right whilst going up means left.", inline=False)
    embed.add_field(name="The two emojies with double arrows represent skirting in either direction. Skirting must be in the opposite direction of the current direction.", value="Direction remains the same for skirting as well.", inline=False)
    embed.add_field(name="If you either vroom in the opposite direction or skirt in the same direction, you die!.", value="You only have one life, so be careful!", inline=False)
    embed.add_field(name="Every 10 successful consecutive turns, the brake option is unlocked for a one time use before needing 15 turns again.", value="The brake action provides a short time period for all alive players to react to an emoji. Anyone who does not will die!", inline=False)
    await ctx.send(embed=embed)
    msg = await ctx.send(f"{ctx.author.mention} is starting a game of vroomskirt! You have 10 seconds to join by reacting here!")
    await msg.add_reaction("✅")
    vsgames[msg.id] = VroomSkirt(ctx, msg, bot)
    await vsgames[msg.id].initGame()


async def tryJoin(payload):
    game = vsgames[payload.message_id]
    if not game.started:
        if payload.member not in game.players:
            game.players.append(payload.member)
            game.alive.append(True)

async def gameLoop(self):
        
        reacts = ["◀️", "▶️", "⏪", "⏩"]
        rightArr = ["▶️", "⏪"]
        leftArr = ["◀️", "⏩"]
        vroom = ["◀️", "▶️"]
        skirt = ["⏪", "⏩"]

        def reactCheck(p):
            return p.user_id == self.players[self.turn].id and (str(p.emoji.name) in reacts or (str(p.emoji.name) == "⏸️" and self.brake)) and p.message_id == self.vroommessage.id

        await self.channel.send("Single arrows represent vrooming in either direction, whilst double arrows skirt in either direction!")
        await self.channel.send("All games must start with a vroom in either direction!")
        time.sleep(3)
        self.vroommessage = await self.channel.send("Game starting here...")
        self.deathmessage = await self.channel.send("Game is ongoing...")
        while self.alive.count(True) > 1:
            if self.brakecount > 10:
                self.brake = True
            time.sleep(1)
            await self.vroommessage.clear_reactions()
            for i in reacts:
                await self.vroommessage.add_reaction(i)
            if self.brake:
                await self.vroommessage.add_reaction("⏸️")
            st = await self.generateMsg()
            await self.vroommessage.edit(content=st)
            try:
                react = await self.client.wait_for("raw_reaction_add", timeout=4, check=reactCheck)
                emote = str(react.emoji.name)
                if emote == "⏸️":
                    waitmsg = await self.channel.send(f"{self.players[self.turn].mention} has started a brake! React to this message with a pause as fast as possible. The last person to react will die along with anyone who doesn't react!")
                    await waitmsg.add_reaction("⏸️")

                    def brakeCheck(p):
                        return p.user_id in [i.id for i in self.players if self.alive[self.players.index(i)]] and str(p.emoji.name) == "⏸️" and p.message_id == waitmsg.id
        
                    while len(self.braked) < self.alive.count(True):
                        try:
                            pause = await self.client.wait_for("raw_reaction_add", timeout=2,check=brakeCheck)
                            if pause.user_id not in self.braked:
                                self.braked.append(pause.user_id)
                        except asyncio.TimeoutError:
                            break
                    for i, v in enumerate(self.players):
                        deadStr = ""
                        if self.alive[i]:
                            if v.id not in self.braked:
                                self.alive[i] = False
                                deadStr += v.mention + " "
                    await self.deathmessage.edit(content=deadStr + " died" if len(deadStr) > 0 else "Everyone survived the brake!")
                    self.brake = False
                    self.brakecount = 0
                elif self.right is None:
                    if emote in skirt:
                        self.alive[self.turn] = False
                        await self.deathmessage.edit(content=f"{self.players[self.turn].mention} has died because you cannot skirt to start the game lmao")
                        self.brake = False
                        self.brakecount = 0
                        time.sleep(2)
                    else:
                        self.right = True if emote in rightArr else False
                        self.brakecount += 1
                elif self.right:
                    if emote in leftArr:
                        self.alive[self.turn] = False
                        await self.deathmessage.edit(content=f"{self.players[self.turn].mention} has gone the wrong direction!")
                        self.brake = False
                        self.brakecount = 0
                        time.sleep(2)
                    else:
                        if emote in skirt:
                            self.right = False
                        self.brakecount += 1
                else:
                    if emote in rightArr:
                        self.alive[self.turn] = False
                        await self.deathmessage.edit(content=f"{self.players[self.turn].mention} has gone the wrong direction!")
                        self.brake = False
                        self.brakecount = 0
                        time.sleep(2)
                    else:
                        if emote in vroom:
                            self.right = True
                        self.brakecount += 1
            except asyncio.TimeoutError:
                await self.deathmessage.edit(content=f"{self.players[self.turn].mention} has taken too long and died!")
                self.alive[self.turn] = False
                self.brake = False
                self.brakecount = 0
                time.sleep(2)
            await self.updateTurn()
        winIndex = self.alive.index(True)
        await self.channel.send(f"{self.players[winIndex].mention} has won the game!")
        time.sleep(3)
        await self.channel.delete()
        embed = discord.Embed(title="Vroomskirt game stats!")
        for i, v in enumerate(self.players):
            embed.add_field(name = v.name + ":", value=" WINNER" if self.alive[i] else " DIED", inline=False)
        await self.ctx.send(embed=embed)
        del vsgames[self.msg.id]