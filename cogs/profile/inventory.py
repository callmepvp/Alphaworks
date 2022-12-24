import discord
import random
import string
from discord.ext import commands
from pymongo import MongoClient
import DiscordUtils

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)
footers = loads(Path("cogs/data/footers.json").read_text())

general = cluster['discord']['general']
recipes = cluster['discord']['recipes']

foraging = cluster['discord']['foraging']
mining = cluster['discord']['mining']
fishing = cluster['discord']['fishing']
mobloot = cluster['discord']['mobloot']
scavenging = cluster['discord']['scavenging']
farming = cluster['discord']['farming']
potions = cluster['discord']['potions']
items = cluster['discord']['items']

categories = ['foraging', 'mining', 'fishing', 'mobloot', 'scavenging', 'farming', 'potions', 'items']

class Inventory(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['inv'])
    async def inventory(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            
            #? Total inv value (bazaar prices)

            #Inventory pages
            inv1=discord.Embed(title = 'Page 1/8: Foraging', description = '', color=0x049a2a)
            inv2=discord.Embed(title = 'Page 2/8: Mining', description = '', color=0x5C615D)
            inv3=discord.Embed(title = 'Page 3/8: Fishing', description = '', color=0x32A5E3)
            inv4=discord.Embed(title = 'Page 4/8: Mob Loot', description = '', color=0xF20B27)
            inv5=discord.Embed(title = 'Page 5/8: Scavenging', description = '', color=0xEA7B0C)
            inv6=discord.Embed(title = 'Page 6/8: Farming', description = '', color=0xD3F20B)
            inv7=discord.Embed(title = 'Page 7/8: Consumables', description = '', color=0xE80BF2)
            inv8=discord.Embed(title = 'Page 8/8: Items', description = '', color=0x0A0A0A)

            embeds = [inv1, inv2, inv3, inv4, inv5, inv6, inv7, inv8]
            for x in embeds:
                x.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
                x.set_footer(text = random.choice(list(footers['en-en'].items()))[1])

            #Paginator Settings
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions = True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")
            paginator.add_reaction('⏭️', "last")

            i = 0
            for inv in embeds:
                category = categories[i]
                directory = cluster['discord'][category] #Get the category to search in

                text = []
                if directory.find_one({'id' : ctx.author.id}) is not None:
                    document = directory.find_one({'id' : ctx.author.id})
                    for res in document:
                        if res != 'id' and res != '_id':
                            resourceAmount = document[res]
                            
                            text.append(f"**{resourceAmount}** x **{string.capwords(res)}**" "\n")
                else:
                    text.append("Empty :(")

                inv.description = ''.join(text)
                i += 1

            await paginator.run(embeds)
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Inventory(client))