import string
from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

general = cluster['discord']['general']
bonuses = cluster['discord']['bonuses']

bonusData = loads(Path("cogs/data/other/bonuses.json").read_text())

class Bonuses(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['bonus', 'buffs', 'debuffs', 'buff', 'debuff'])
    async def bonuses(self, ctx, *, bonus = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        text = []

        if statsGeneral is not None:
            statsBonuses = bonuses.find_one({'id' : ctx.author.id})

            #If bonus wasn't given
            if bonus is None:
                text.append("*f!bonus BONUS_NAME for specifics!*" "\n")
                if statsBonuses is not None:
                    document = bonuses.find_one({'id' : ctx.author.id})
                    for res in document:
                        if res != 'id' and res != '_id':

                            text.append(f'{string.capwords(res)} ⇒ +**5%** evasion chance for **{statsBonuses["well-fed"]}** hunt(s)!' '\n')
                else:
                    text.append("You have no bonuses currently. Get bonuses by eating or drinking potions!")

            #Bonus search-up
            elif bonus is not None:
                bonusD = list(bonusData[str(bonus)].items())

                text.append(f"**{string.capwords(bonus)}** ⇒ {bonusD[1][1]}")

            await ctx.send(''.join(text))
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Bonuses(client))