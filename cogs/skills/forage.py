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
foraging = cluster['discord']['foraging']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']

data = loads(Path("cogs/data/items/forage.json").read_text())

#Random resource selection
def returnData(pwr):
    ap = "AP" + str(pwr)
    woodTypes = data[ap][0]
    x = json.dumps(woodTypes)
    y = json.loads(x)

    z = str(random.randrange(int(len(y))))

    return y[z]

class Forage(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases=['chop', 'lumber'])
    async def forage(self, ctx):
       
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsSkills = skills.find_one({'id' : ctx.author.id})
            statsForaging = foraging.find_one({'id' : ctx.author.id})
            statsCollections = collections.find_one({'id' : ctx.author.id})

            woodAmount = random.randint(1, 2)
            
            #Choose the resources
            if statsGeneral['axepower'] == 1:
                woodType = returnData(1)
                xp = 3 * woodAmount
            elif statsGeneral['axepower'] == 2:
                woodType = returnData(2)
                xp = 5 * woodAmount
            elif statsGeneral['axepower'] >= 3:
                woodType = returnData(3)
                xp = 7 * woodAmount

            #Update inventory
            if foraging.find_one({'id' : ctx.author.id, woodType : {'$exists': True}}) is None:
                woodData = {
                    'id' : ctx.author.id,
                    woodType : woodAmount
                }

                if statsForaging is None:
                    foraging.insert_one(woodData)
                else:
                    foraging.update_one({'id' : ctx.author.id}, {"$set":{woodType : woodAmount}})
                
            else:
                foraging.update_one({'id' : ctx.author.id}, {"$set":{woodType : statsForaging[woodType] + woodAmount}})

            await ctx.send(f'You chopped wood! You gained **{woodAmount}** x **{string.capwords(woodType)}** wood.')

            #Give the skill XP
            existingXP = statsSkills['foragingXP']
            existingLevel = statsSkills['foragingLevel']
            forageXP = existingXP + xp
            
            if forageXP >= 50*existingLevel + 10:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'foragingXP' : 0, 'foragingLevel' : existingLevel + 1}})
                await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Foraging** level **{existingLevel + 1}**!')
            else:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'foragingXP' : forageXP}})
                await ctx.send(f'**[*]** You gained +**{xp} Foraging** XP!')

            #Give collection
            collections.update_one({'id' : ctx.author.id}, {"$set":{'wood' : statsCollections['wood'] + woodAmount}})
            collections.update_one({'id' : ctx.author.id}, {"$set":{'woodtemp' : statsCollections['woodtemp'] + woodAmount}})

            if statsCollections['woodtemp'] + woodAmount >= statsCollections['woodmilestone']*50 + 50 and statsCollections['woodmilestone'] >= 0:
                collections.update_one({'id' : ctx.author.id}, {"$set":{'woodmilestone' : statsCollections['woodmilestone'] + 1}})
                collections.update_one({'id' : ctx.author.id}, {"$set":{'woodtemp' : 0 + (statsCollections['woodtemp'] + woodAmount) - (statsCollections['woodmilestone']*50 + 50)}})
                
                message = []
                message.append('**[COLLECTION]** **Wood** Collection leveled up!')

                #Give collection rewards
                if statsCollections['woodmilestone'] + 1 == 1:
                    message.append(' You unlocked the **Tool Rod** recipe. You unlocked the **Copper Axe** recipe.')
                    recipes.update_one({'id' : ctx.author.id}, {"$set":{'toolrod' : True, 'copperaxe' : True}})
                
                messageValue = ''.join(message)
                await ctx.send(messageValue)
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Forage(client))