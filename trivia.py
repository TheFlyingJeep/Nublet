from pytrivia import Trivia, Category, Diffculty, Type
import asyncio, time, random, discord, inspect
api_req = Trivia(True)
trivia_games = {}
with open("categories.txt", "r") as cats:
    categories = cats.read().splitlines()
cat_map = Category.__dict__["_member_map_"]
diff_map = Diffculty.__dict__["_member_map_"]
diffs = ["Easy", "Medium", "Hard"]

class TriviaGame:
    
    def __init__(self, ctx, client, msg)->None:
        self.ctx = ctx
        self.client = client
        self.msg = msg
        self.skipped = False
        self.joining = False
        self.temp_channel = None
        self.players = [ctx.author]
        self.scores = [0]
        self.curturn = 0
        self.question = None
        self.correct_answer = None
        self.no_answer_count = 0
        
    async def prepare_game(self):
        self.joining = True
        for i in range(1,20):
            time.sleep(1)
            await self.msg.edit(content=f"{self.ctx.author.mention} is starting a trivia game! You have {20-i} seconds to join by reacting with a ✅.\nThe game originator can skip the countdown by reacting with a ⏩")
            if self.skipped:
                break
        if len(self.players) > 1:
            self.joining = False
            await self.msg.edit(content=f"This game has already started")
            self.channel = await self.msg.guild.create_text_channel(f"Trivia-game-{self.msg.id}")
            st = ""
            for i in self.players:
                st += i.mention + " "
            st += "\nFirst player to meet or exceed 9 points wins"
            await self.channel.send(st)
            await self.gameplay()
        else:
            await self.msg.edit(content="There were not enough players to start this game")
            del trivia_games[self.msg.id]
            
    async def get_question(self, cat, diff):
        return api_req.request(1, cat, diff, Type.Multiple_Choice)
    
    async def tryAnswer(self, ans, answers, points):
        if answers[ans].lower() == self.correct_answer.lower():
            await self.channel.send(f"{self.players[self.curturn].mention} has guessed the correct answer!")
            self.scores[self.curturn] += points
        else:
            await self.channel.send(f"{self.players[self.curturn].mention} has guessed incorrectly! The correct answer was {self.correct_answer}")
            
    async def updateTurn(self):
        self.curturn += 1
        if self.curturn >= len(self.players):
            self.curturn = 0
            
    async def end_game(self):
        del trivia_games[self.msg.id]
    
    async def gameplay(self):
        answers = {}
        cats = {}
        
        def cat_check(p):
            return p.author == self.players[self.curturn] and p.channel == self.channel and (p.content.strip().isnumeric() and int(p.content.strip()) in cats)
        
        def answer_check(p):
            return p.author == self.players[self.curturn] and p.channel == self.channel and p.content.lower().strip() in answers
        
        def diff_check(p):
            return p.author == self.players[self.curturn] and p.channel == self.channel and (p.content.strip().isnumeric() and int(p.content.strip()) in range(1,4))
        
        while max(self.scores) < 9:
            await self.channel.send(f"It is now {self.players[self.curturn].mention}'s turn")
            cats = {}
            points = 0
            answers = {}
            category = None
            difficulty = None
            answered = False
            cat_msg = "Please pick your category by typing 1, 2, or 3: \n"
            i = 0
            temp = []
            while i < 3:
                cat = random.randint(0,23)
                if cat not in temp:
                    cats[i+1] = categories[cat]
                    temp.append(cat)
                    cat_msg += f"{i+1}: {categories[cat].replace('_', ' ')}\n"
                    i+=1
            await self.channel.send(cat_msg)
            progressed = False
            try:
                cat_select = await self.client.wait_for("message", timeout=10, check=cat_check)
                category = cat_map[cats[int(cat_select.content.strip())]]
                progressed = True
            except asyncio.TimeoutError:
                await self.channel.send("Player took too long!")
            if progressed:
                progressed_further = False
                await self.channel.send("Please select the difficulty you want:\n1: Easy (1 point)\n2: Medium (2 points)\n3: Hard (3 points)")
                try:
                    diff_select = await self.client.wait_for("message", timeout=10, check=diff_check)
                    difficulty = diff_map[diffs[int(diff_select.content.strip())-1]]
                    points = int(diff_select.content.strip())
                    progressed_further = True
                except asyncio.TimeoutError:
                    await self.channel.send("Player took too long")
                if progressed_further:
                    question = await self.get_question(category, difficulty)
                    await self.channel.send(question["results"][0]["question"])
                    whereAns = random.randint(0, 3)
                    st = "Answers are: \n"
                    addedCorrect = False
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
                        msg = await self.client.wait_for("message", timeout=20, check=answer_check)
                        await self.tryAnswer(msg.content.lower().strip(), answers, points)
                        answered = True
                    except asyncio.TimeoutError:
                        await self.channel.send(f"{self.players[self.curturn].mention} failed to answer the question in time. The correct answer is " + self.correct_answer)
            if not answered:
                self.no_answer_count += 1
            else:
                self.no_answer_count = 0
            if self.no_answer_count >= len(self.players):
                await self.channel.send("No one played for a whole round, game ending!")
                break
            emb = discord.Embed(title="Trivia game scores")
            for i, v in enumerate(self.players):
                emb.add_field(name=v.name + ":", value="Score: " + str(self.scores[i]), inline=False)
            await self.channel.send(embed=emb)
            await self.updateTurn()
            time.sleep(2)
        ind = self.scores.index(max(self.scores))
        if max(self.scores) == 0:
            await self.channel.send("Everybody is a loser!")
        else:
            await self.channel.send(f"Game over! The winner was {self.players[ind].mention}")
        time.sleep(1)
        embed = discord.Embed(title="Trivia game scores")
        if self.scores.count(0) == len(self.scores):
            for i, v in enumerate(self.players):
                scoreStr = "Score: " + str(self.scores[i])
                embed.add_field(name=v.name + ":", value=scoreStr, inline=False)
            embed.add_field(name="Everybody is lameeee", value="Seriously, no points?")
        else:
            for i, v in enumerate(self.players):
                scoreStr = "Score: " + str(self.scores[i])
                scoreStr += " - WINNER" if i == ind else ""
                embed.add_field(name=v.name + ":", value=scoreStr, inline=False)
        await self.channel.delete()
        await self.msg.edit(content="This game has ended!")
        await self.ctx.send(embed=embed)
        await self.end_game()

async def prompt_players(ctx, bot):
    msg = await ctx.send(f"{ctx.author.mention} is starting a trivia game! You have 20 seconds to join by reacting with a ✅.\nThe game originator can skip the countdown by reacting with a ⏩")
    await msg.add_reaction("✅")
    await msg.add_reaction("⏩")
    trivia_games[msg.id] = TriviaGame(ctx, bot, msg)
    await trivia_games[msg.id].prepare_game()
            
async def try_join(payload):
    game = trivia_games[payload.message_id]
    if game.joining and payload.member not in game.players:
        game.players.append(payload.member)
        game.scores.append(0)
        
async def try_start(payload):
        game = trivia_games[payload.message_id]
        if (game.joining and payload.member == game.ctx.author):
            game.skipped = True