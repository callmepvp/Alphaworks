import string
import random

from discord.ext import commands
from pymongo import MongoClient

import json
from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

#Collections
general = cluster['discord']['general']
scavenging = cluster['discord']['scavenging']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']

data = loads(Path("cogs/data/items/scavenging.json").read_text())

#Random resource selection
def returnData(pwr):
    s = "S" + str(pwr)
    scavengeTypes = data[s][0]
    x = json.dumps(scavengeTypes)
    y = json.loads(x)

    z = str(random.randrange(int(len(y))))

    return y[z]
    
class Scavenging(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['scavange', 'gather', 'scavanging'])
    async def scavenge(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsScavenging = scavenging.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})

            scavengeAmount = random.randint(1, 2)
            scavengeType = returnData(1)
            xp = 4 * scavengeAmount

            #Update inventory           
            if scavenging.find_one({'id' : ctx.author.id, scavengeType : {'$exists': True}}) is None:
                scavengeData = {
                    'id' : ctx.author.id,
                    scavengeType : scavengeAmount
                }

                if statsScavenging is None:
                    scavenging.insert_one(scavengeData)
                else:
                    scavenging.update_one({'id' : ctx.author.id}, {"$set":{scavengeType : scavengeAmount}})
            else:
                scavenging.update_one({'id' : ctx.author.id}, {"$set":{scavengeType : statsScavenging[scavengeType] + scavengeAmount}})

            await ctx.send(f'You went out to scavenge! You gained **{scavengeAmount}** x **{string.capwords(scavengeType)}**.')

            #Calculate and give the skill XP
            existingXP = statsSkills['scavengingXP']
            existingLevel = statsSkills['scavengingLevel']
            existingAttribute = statsSkills['scavengingAttribute']
            scavengingXP = existingXP + xp
            
            if scavengingXP >= 50*existingLevel + 10:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'scavengingXP' : 0, 'scavengingLevel' : existingLevel + 1, 'scavengingAttribute' : existingAttribute + 1}})
                await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Scavenging** level **{existingLevel + 1}**! \n**[*]** Your evasion bonus is now: **{existingAttribute}** ⇒ **{existingAttribute + 1}**')
            else:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'scavengingXP' : scavengingXP}})
                await ctx.send(f'**[*]** You gained +**{xp} Scavenging** XP!')
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Scavenging(client))