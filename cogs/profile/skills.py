import math
import string
import random
import discord
from discord.ext import commands
from pymongo import MongoClient
import DiscordUtils

from json import loads
from pathlib import Path

#Retrieve tokens
footers = loads(Path("cogs/data/footers.json").read_text())
skillsData = loads(Path("cogs/data/other/skills.json").read_text())

data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

general = cluster['discord']['general']
skills = cluster['discord']['skills']

class Skills(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['skill'])
    async def skills(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsSkills = skills.find_one({'id' : ctx.author.id})

            #Pages
            page1 = discord.Embed(title = "Foraging", description = "", color = 0x00e600)
            page2 = discord.Embed(title = "Mining", description = "", color = 0xc2c2d6)
            page3 = discord.Embed(title = "Fishing", description = "", color = 0x0000ff)
            page4 = discord.Embed(title = "Combat", description = "", color = 0xff0000)
            page5 = discord.Embed(title = "Scavenging", description = "", color = 0xe6ff99)
            page6 = discord.Embed(title = "Farming", description = "", color = 0xffff1a)
            page7 = discord.Embed(title = "Brewing", description = "", color = 0xcc00cc)
            page8 = discord.Embed(title = "Cooking", description = "", color = 0x804000)
            page9 = discord.Embed(title = "Crafting", description = "", color = 0x000000)

            pages = [page1, page2, page3, page4, page5, page6, page7, page8, page9]
            skill = ['foraging', 'mining', 'fishing', 'combat', 'scavenging', 'farming', 'brewing', 'cooking', 'crafting']

            var = 0
            for x in pages:
                x.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
                x.set_footer(text = random.choice(list(footers['en-en'].items()))[1])

                #Set the image and description of each embed
                description = f"{list(skillsData[f'{skill[var]}'].items())[0][1]}"
                url = f"{list(skillsData[f'{skill[var]}'].items())[1][1]}"

                x.description = description
                x.set_image(url = f'attachment://{url}')

                var += 1

            #Paginator Settings
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions = True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")
            paginator.add_reaction('⏭️', "last")

            await paginator.run(pages)

            """
            for category in categories:
                bar = []
                if statsSkills[category + 'XP']/(50*statsSkills[category + 'Level'] + 10) == 0:
                    for x in range(10):
                        bar.append('□')
                else:
                    counter = 0
                    for x in range(math.ceil((statsSkills[category + 'XP']/(50*statsSkills[category + 'Level'] + 10)) * 10)):
                        bar.append('■')
                        counter += 1

                    for j in range(10-counter):
                        bar.append('□')
                
                bar = ''.join(bar)
                pos = categories.index(category)

                text.append(f"⇒ **{string.capwords(category)}** Level **{statsSkills[category + 'Level']}** | **{statsSkills[category + 'XP']}**/**{50*statsSkills[category + 'Level'] + 10}** XP | {bar} | {descriptions[pos]}: **+{statsSkills[category + 'Attribute']}**" "\n")

            await ctx.send(''.join(text))"""

        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Skills(client))