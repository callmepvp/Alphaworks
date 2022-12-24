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
farming = cluster['discord']['farming']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']

data = loads(Path("cogs/data/items/farming.json").read_text())

#Random resource selection
def returnData(pwr):
    f = "F" + str(pwr)
    farmTypes = data[f][0]
    x = json.dumps(farmTypes)
    y = json.loads(x)

    z = str(random.randrange(int(len(y))))

    return y[z]
    
class Farming(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['harvest'])
    async def farm(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsFarming = farming.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})

            farmAmount = random.randint(1, 2)
            farmType = returnData(1)
            xp = 4 * farmAmount

            #Update inventory  
            if farming.find_one({'id' : ctx.author.id, farmType : {'$exists': True}}) is None:
                farmData = {
                    'id' : ctx.author.id,
                    farmType : farmAmount
                }

                if statsFarming is None:
                    farming.insert_one(farmData)
                else:
                    farming.update_one({'id' : ctx.author.id}, {"$set":{farmType : farmAmount}})
            else:
                farming.update_one({'id' : ctx.author.id}, {"$set":{farmType : statsFarming[farmType] + farmAmount}})

            await ctx.send(f'You farmed the nearby fields! You gained **{farmAmount}** x **{string.capwords(farmType)}**.')

            #Calculate and give the skill XP
            existingXP = statsSkills['farmingXP']
            existingLevel = statsSkills['farmingLevel']
            existingAttribute = statsSkills['farmingAttribute']
            farmingXP = existingXP + xp
            
            if farmingXP >= 50*existingLevel + 10:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'farmingXP' : 0, 'farmingLevel' : existingLevel + 1, 'farmingAttribute' : existingAttribute + 4}})
                general.update_one({'id' : ctx.author.id}, {"$set":{'maxhp' : statsGeneral['maxhp'] + 4}})
                await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Farming** level **{existingLevel + 1}**! \n**[*]** Your Max HP bonus is now: **{existingAttribute}** ⇒ **{existingAttribute + 4}**')

            else:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'farmingXP' : farmingXP}})
                await ctx.send(f'**[*]** You gained +**{xp} Farming** XP!')
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Farming(client))