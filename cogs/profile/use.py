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

class Use(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['u'])
    async def use(self, ctx, bonus = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        text = []

        if statsGeneral is not None:
            pass
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Use(client))