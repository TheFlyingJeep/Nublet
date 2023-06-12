from pytrivia import Trivia, Category, Diffculty, Type
import asyncio, time, random, discord
api_req = Trivia(True)
trivia_games = {}

class TriviaQuestion:
    def __init__(self, ctx, msg, client) -> None:
        self.ctx = ctx
        self.msg = msg
        self.client = client
        self.started = False
        self.players = [ctx.author]
        self.channel = None
        self.scores = [0]
        self.turn = 0
        self.correct_answer = ""

    async def joinLoop(self):
        for i in range(1,20):
            time.sleep(1)
            await self.msg.edit(content=f"{self.ctx.author.mention} is starting a trivia game! You have {20-i} seconds to join by reacting to this message")
        if len(self.players) > 1:
            await self.msg.edit(content="This game has already started. You can start a new one with ;trivia!")
            self.started = True
            self.channel = await self.msg.guild.create_text_channel(f"Trivia-game-{self.msg.id}")
            st = ""
            for i in self.players:
                st += i.mention + " "
            await self.channel.send(st)
            loop = asyncio.get_event_loop()
            gameTask = loop.create_task(gameLoop(self))
            await gameTask
        else:
            await self.msg.edit(content="There are not enough players to start this game")
            del trivia_games[self.msg.id]

    async def updateTurn(self):
        self.turn += 1
        if self.turn >= len(self.players):
            self.turn = 0

    async def askQuestion(self):
        return api_req.request(1, None, None, None)
    
    async def tryAnswer(self, ans, answers):
        if answers[ans].lower() == self.correct_answer.lower():
            await self.channel.send(f"{self.players[self.turn].mention} has guessed the correct answer!")
            self.scores[self.turn] += 1
        else:
            await self.channel.send(f"{self.players[self.turn].mention} has guessed incorrectly! The correct answer was {self.correct_answer}")

    async def endThread(self):
        del trivia_games[self.msg.id]

async def startGame(ctx, bot):
    msg = await ctx.send(f"{ctx.author.mention} is starting a trivia game! You have 20 seconds to join by reacting to this message")
    await msg.add_reaction("✅")
    trivia_games[msg.id] = TriviaQuestion(ctx, msg, bot)
    await trivia_games[msg.id].joinLoop()

async def tryJoin(payload):
    game = trivia_games[payload.message_id]
    if not game.started:
        if payload.member not in game.players:
            game.players.append(payload.member)
            game.scores.append(0)

async def gameLoop(self):
        answers = {}

        def ansCheck(p):
            return p.author == self.players[self.turn] and p.channel == self.channel and p.content.lower().strip() in answers

        while max(self.scores) < 5:
            await self.channel.send(f"It is currently {self.players[self.turn].mention}'s turn")
            question = await self.askQuestion()
            await self.channel.send(question["results"][0]["question"])
            whereAns = random.randint(0, 3)
            st = "Answers are: \n"
            addedCorrect = False
            answers = {}
            abcd = ["a", "b", "c", "d"]
            l = 0
            for i, v in enumerate(question["results"][0]["incorrect_answers"]):
                if i == whereAns:
                    answers[abcd[l]] = question["results"][0]["correct_answer"]
                    st += abcd[l].upper() + ": " + question["results"][0]["correct_answer"] + "\n"
                    l += 1
                    addedCorrect = True
                answers[abcd[l]] = question["results"][0]["incorrect_answers"][i]
                st += abcd[l].upper() + ": " + v + "\n"
                l += 1
            if not addedCorrect:
                answers[abcd[l]] = question["results"][0]["correct_answer"]
                st += abcd[l].upper() + ": " + question["results"][0]["correct_answer"] + "\n"
            await self.channel.send(st)
            self.correct_answer = question["results"][0]["correct_answer"]
            try:
                msg = await self.client.wait_for("message", timeout=20, check=ansCheck)
                await self.tryAnswer(msg.content.lower().strip(), answers)
            except asyncio.TimeoutError:
                await self.channel.send(f"{self.players[self.turn].mention} failed to answer the question in time. The correct answer is " + self.correct_answer)
            finally:
                emb = discord.Embed(title="Trivia game scores")
                for i, v in enumerate(self.players):
                    emb.add_field(name=v.name + ":", value="Score: " + str(self.scores[i]), inline=False)
                await self.channel.send(embed=emb)
                await self.updateTurn()
                time.sleep(2)
        ind = self.scores.index(5)
        await self.channel.send(f"Game over! The winner was {self.players[ind].mention}")
        time.sleep(1)
        embed = discord.Embed(title="Trivia game scores")
        for i, v in enumerate(self.players):
            scoreStr = "Score: " + str(self.scores[i])
            scoreStr += " - WINNER" if self.scores[i] == 5 else ""
            embed.add_field(name=v.name + ":", value=scoreStr, inline=False)
        await self.channel.delete()
        await self.ctx.send(embed=embed)
        await self.endThread()