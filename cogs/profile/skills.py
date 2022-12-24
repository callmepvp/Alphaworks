import math
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
skills = cluster['discord']['skills']

#! TRY USING EMBED
class Skills(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['skill'])
    async def skills(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsSkills = skills.find_one({'id' : ctx.author.id})

            text = []
            text.append("**Your Skills:**" "\n" "\n")

            categories = ['foraging', 'mining', 'fishing', 'combat', 'scavenging', 'farming', 'brewing', 'cooking', 'crafting']
            descriptions = ['Strength Bonus',
                            'Defense Bonus',
                            'Max HP Bonus',
                            'Damage Bonus',
                            'Evasion Bonus',
                            'Max HP Bonus',
                            'Time Reduction',
                            'Time Reduction',
                            'Less Resources']

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

            await ctx.send(''.join(text))
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Skills(client))