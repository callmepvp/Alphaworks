import random
from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

#Collections
general = cluster['discord']['general']

class Gambling(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    #Add a coin flipping coin animation before showing the result
    @commands.command(aliases = ['flip', 'cf'])
    async def coinflip(self, ctx, side = None, amount = 1):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            if side == None:
                await ctx.send("Please input a valid side (t/h)")
            elif side == 't':
                if amount == None:
                    await ctx.send("Please input a valid amount to bet.")
                elif int(amount) <= statsGeneral['coins']:
                    chance = random.randint(1, 2)
                    if chance == 1:
                        await ctx.send(f'**[*]** You bet on tails and won! +**{int(amount)*2}** Coins!')
                        general.update_one({'id' : ctx.author.id}, {"$set":{'coins' : statsGeneral['coins'] + int(amount)*2}})
                    else:
                        await ctx.send('**[*]** You bet on tails and lost. :(')
                        general.update_one({'id' : ctx.author.id}, {"$set":{'coins' : statsGeneral['coins'] - int(amount)}})
                else:
                    await ctx.send("You don't have enough coins for this.")
            elif side == 'h':
                if amount == None:
                    await ctx.send("Please input a valid amount to bet.")
                elif int(amount) <= statsGeneral['coins']:
                    chance = random.randint(1, 2)
                    if chance == 2:
                        await ctx.send(f'**[*]** You bet on heads and won! +**{int(amount)*2}** Coins!')
                        general.update_one({'id' : ctx.author.id}, {"$set":{'coins' : statsGeneral['coins'] + int(amount)*2}})
                    else:
                        await ctx.send('**[*]** You bet on heads and lost. :(')
                        general.update_one({'id' : ctx.author.id}, {"$set":{'coins' : statsGeneral['coins'] - int(amount)}})
                else:
                    await ctx.send("You don't have enough coins for this.")
            else:
                await ctx.send("Please input a valid side (t/h)")
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Gambling(client))