from discord.ext import commands
import discord
import random

from json import loads
from pathlib import Path

footers = loads(Path("cogs/data/footers.json").read_text())
footer = random.choice(list(footers['en-en'].items()))[1] #! Only returns ENGLISH footers ('en-en')

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):

        #Revamp
        descValue = []
        descValue.append("If you're having trouble, please contact me personally `pvp#7272` or join the Discord server: ..." "\n"
                    "*Run the setup command if you want to create a profile!*" "\n" "\n") 
        descValue.append("**Skill Commands**" "\n" "`mine` `forage` `fish` `farm` `scavenge` `hunt` `craft` `cook` `brew`" "\n"
                    "**Economy Commands**" "\n" "`coinflip`" "\n"
                    "**Character Commands**" "\n" "`bestiary` `collections` `skills` `inventory` `bonuses` `recipe`" "\n"
                    "**Misc Commands**" "\n" "`help` `leaderboard`" "\n"
                    "*Type help <command> for usage info.*")
        
        desc = ''.join(descValue)
        embed = discord.Embed(title = "Command Help", description = desc, color = 0x1243d9)
        embed.set_footer(text = "Don't be shy to ask for help!")

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))