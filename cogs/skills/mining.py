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
mining = cluster['discord']['mining']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']

data = loads(Path("cogs/data/items/mining.json").read_text())

#Random resource selection
def returnData(pwr):
    pp = "PP" + str(pwr)
    mineTypes = data[pp][0]
    x = json.dumps(mineTypes)
    y = json.loads(x)

    z = str(random.randrange(int(len(y))))

    return y[z]
    
class Mining(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command()
    async def mine(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsSkills = skills.find_one({'id' : ctx.author.id})
            statsMining = mining.find_one({'id' : ctx.author.id})
            statsCollections = collections.find_one({'id' : ctx.author.id})

            mineAmount = random.randint(1, 3)

            #Choose the resources
            if statsGeneral['pickpower'] == 1:
                mineType = returnData(1)
                xp = 3 * mineAmount
            elif statsGeneral['pickpower'] == 2:
                mineType = returnData(2)
                xp = 6 * mineAmount
            elif statsGeneral['pickpower'] >= 3:
                mineType = returnData(3)
                xp = 9 * mineAmount

            #Update inventory
            if mining.find_one({'id' : ctx.author.id, mineType : {'$exists': True}}) is None:
                mineData = {
                    'id' : ctx.author.id,
                    mineType : mineAmount
                }

                if statsMining is None:
                    mining.insert_one(mineData)
                else:
                    mining.update_one({'id' : ctx.author.id}, {"$set":{mineType : mineAmount}})
            else:
                mining.update_one({'id' : ctx.author.id}, {"$set":{mineType : statsMining[mineType] + mineAmount}})

            await ctx.send(f'You mined ore! You gained **{mineAmount}** x **{string.capwords(mineType)}**.')

            #Give the skill xp
            existingXP = statsSkills['miningXP']
            existingLevel = statsSkills['miningLevel']
            existingAttribute = statsSkills['miningAttribute']
            miningXP = existingXP + xp
            
            if miningXP >= 50*existingLevel + 10:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'miningXP' : 0, 'miningLevel' : existingLevel + 1,  'miningAttribute' : existingAttribute + 2}})
                general.update_one({'id' : ctx.author.id}, {"$set":{'defense' : statsGeneral['defense'] + 2}})
                await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Mining** level **{existingLevel + 1}**! \n**[*]** Your defense bonus is now: **{existingAttribute}** ⇒ **{existingAttribute + 2}**')

            else:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'miningXP' : miningXP}})
                await ctx.send(f'**[*]** You gained +**{xp} Mining** XP!')

            #Give collection
            collections.update_one({'id' : ctx.author.id}, {"$set":{'ore' : statsCollections['ore'] + mineAmount}})
            collections.update_one({'id' : ctx.author.id}, {"$set":{'oretemp' : statsCollections['oretemp'] + mineAmount}})

            if statsCollections['ore'] + mineAmount >= statsCollections['oremilestone']*50 + 50 and statsCollections['oremilestone'] >= 0:
                collections.update_one({'id' : ctx.author.id}, {"$set":{'oremilestone' : statsCollections['oremilestone'] + 1}})
                #collections.update_one({'id' : ctx.author.id}, {"$set":{'oretemp' : 0 + (statsCollections['oretemp'] + mineAmount) - (statsCollections['oremilestone']*50 + 50)}})
                
                message = []
                message.append('**[COLLECTION]** **Ore** Collection leveled up!')

                #Give collection rewards
                if statsCollections['oremilestone'] + 1 == 1:
                    message.append(' You unlocked the **Copper Pickaxe** recipe.')
                    recipes.update_one({'id' : ctx.author.id}, {"$set":{'copper pickaxe' : True}})
                
                messageValue = ''.join(message)
                await ctx.send(messageValue)
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Mining(client))