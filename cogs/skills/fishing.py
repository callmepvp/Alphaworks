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
fishing = cluster['discord']['fishing']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']
areas = cluster['discord']['areas']

data = loads(Path("cogs/data/items/fishing.json").read_text())

#II option: make a series (seeria) formula for each chance (3) and plug that into the if (finding the n-th items chances)

#Random resource selection
# 1 - 40, 59, 1
# 2 - 42, 56, 2
# 3 - 44, 53, 3

# n > +2, -3, +1

# 10 > 58, 33, 10

#Catch fish data
def returnData(val):

    f = "F" + str(val)

    fishTypes = data[f][0]
    x = json.dumps(fishTypes)
    y = json.loads(x)

    z = str(random.randrange(int(len(y))))

    return y[z]
        
class Fishing(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command()
    async def fish(self, ctx):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsFishing = fishing.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})
            statsAreas = areas.find_one({'id' : ctx.author.id})

            fishAmount = random.randint(1, 2)
            
            #Choose the resources
            TreasureCatch = False
            pwr = statsGeneral['fishingrodpower']
            chance = random.randint(1, 102)
            if chance > 61-(pwr*2)+2: #Fish
                
                #!!!Maybe a way to make it better!!!
                currentlocation = statsAreas['currentlocation']
                if currentlocation == 'pond':
                    fishType = returnData(2)
                    xp = 2 * fishAmount
                else:
                    fishType = returnData(3)
                    xp = 4 * fishAmount

            elif chance <= 61-(pwr*2)+2 and chance > 1+pwr-1: #Trash
                fishType = returnData(1)
                xp = 1 * fishAmount

            elif chance >= 1+pwr-1 and chance <= 1+pwr-1: #Treasure
                TreasureCatch = True
                fishType = returnData(0)
                xp = 20

            message = []
            if fishing.find_one({'id' : ctx.author.id, fishType : {'$exists': True}}) is None:
                fishData = {
                    'id' : ctx.author.id,
                    fishType : fishAmount
                }

                if statsFishing is None:
                    fishing.insert_one(fishData)
                else:
                    fishing.update_one({'id' : ctx.author.id}, {"$set":{fishType : fishAmount}})
            else:
                fishing.update_one({'id' : ctx.author.id}, {"$set":{fishType : statsFishing[fishType] + fishAmount}})
            
            #Form the right message
            if TreasureCatch == False:
                message.append(f'You fished! You gained **{fishAmount}** x **{string.capwords(fishType)}**.' '\n')
            else:
                message.append(f'**[TREASURE]**You fished! You gained **{fishAmount}** x **{string.capwords(fishType)}**!' '\n')

            messageValue = ''.join(message)
            await ctx.send(messageValue)

            existingXP = statsSkills['fishingXP']
            existingLevel = statsSkills['fishingLevel']
            existingAttribute = statsSkills['fishingAttribute']
            fishingXP = existingXP + xp
            
            if fishingXP >= 50*existingLevel + 10:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'fishingXP' : 0, 'fishingLevel' : existingLevel + 1, 'fishingAttribute' : existingAttribute + 4}})
                general.update_one({'id' : ctx.author.id}, {"$set":{'maxhp' : statsGeneral['maxhp'] + 4}})
                await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Fishing** level **{existingLevel + 1}**! \n**[*]** Your Max HP bonus is now: **{existingAttribute}** ⇒ **{existingAttribute + 4}**')

            else:
                skills.update_one({'id' : ctx.author.id}, {"$set":{'fishingXP' : fishingXP}})
                await ctx.send(f'**[*]** You gained +**{xp} Fishing** XP!')
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Fishing(client))