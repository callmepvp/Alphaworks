import string
import random
from tabnanny import check

from discord.ext import commands
from pymongo import MongoClient

import json
from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

data = loads(Path("cogs/data/recipes/brewingRecipes.json").read_text())

#Collections
general = cluster['discord']['general']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']
items = cluster['discord']['items']
tools = cluster['discord']['tools']
potions = cluster['discord']['potions']

foraging = cluster['discord']['foraging']
mining = cluster['discord']['mining']
mobloot = cluster['discord']['mobloot']
scavenging = cluster['discord']['scavenging']
farming = cluster['discord']['farming']

#Return the current directory
def returnDir(y, digit):
    if y["d" + str(digit)] == 'foraging':
        dir = foraging
    elif y["d" + str(digit)] == 'scavenging':
        dir = scavenging
    elif y["d" + str(digit)] == 'mobloot':
        dir = mobloot
    elif y["d" + str(digit)] == 'farming':
        dir = farming
    
    return dir
    
class Brewing(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command()
    async def brew(self, ctx, item, amount = 1):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsPotions = potions.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})

            brewSuccess = False
            try:
                dat = data[item][0]
                x = json.dumps(dat)
                y = json.loads(x)
            except:
                await ctx.send("This recipe wasn't found.")
                return

            if recipes.find_one({'id' : ctx.author.id, item : {'$exists': True}}) is not None: #If recipe exists

                #Check resources
                checkedRes = 0
                for i in range(int(len(y)/3)):
                    dir = returnDir(y, i)

                    if dir.find_one({'id' : ctx.author.id, y[str(i)] : {'$exists': True}}):
                        if dir.find_one({'id' : ctx.author.id})[y[str(i)]] >= amount * int(y["r" + str(i)]):
                            checkedRes += 1

                        if checkedRes == int(len(y)/3):
                            brewSuccess = True
                            for j in range(checkedRes):
                                dir = returnDir(y, j)

                                if dir.find_one({'id' : ctx.author.id})[y[str(j)]] - amount * int(y["r" + str(j)]) != 0:
                                    dir.update_one({'id' : ctx.author.id}, {"$set":{y[str(j)] : dir.find_one({'id' : ctx.author.id})[y[str(j)]] - amount * int(y["r" + str(j)])}})
                                else:
                                    dir.update_one({'id' : ctx.author.id}, {'$unset' : {y[str(j)] : ''}})
                                    
                if brewSuccess == False:
                    await ctx.send("You don't have enough resources to brew this!")
                
                else:

                    #Give the item
                    if potions.find_one({'id' : ctx.author.id, item : {'$exists': True}}) is None:
                        brewData = {
                            'id' : ctx.author.id,
                            item : amount
                        }

                        if statsPotions is None:
                            potions.insert_one(brewData)
                        else:
                            potions.update_one({'id' : ctx.author.id}, {"$set":{item : amount}})
                    else:
                        potions.update_one({'id' : ctx.author.id}, {"$set":{item : statsPotions[item] + amount}})

                    await ctx.send(f'You did some brewing! You gained **{amount}** x **{string.capwords(item)}**.')

                    #Calculate the skill XP
                    existingXP = statsSkills['brewingXP']
                    existingLevel = statsSkills['brewingLevel']

                    #Calculate given XP based on ingredient amount
                    xp = 1 * amount
                    for w in range(int(len(y)/3)):
                        xp = xp * int(y["r" + str(w)])

                    brewingXP = existingXP + xp
                    
                    if brewingXP >= 50*existingLevel + 10:
                        skills.update_one({'id' : ctx.author.id}, {"$set":{'brewingXP' : 0, 'brewingLevel' : existingLevel + 1}})
                        await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Brewing** level **{existingLevel + 1}**!')

                    else:
                        skills.update_one({'id' : ctx.author.id}, {"$set":{'brewingXP' : brewingXP}})
                        await ctx.send(f'**[*]** You gained +**{xp} Brewing** XP!')
            else:
                await ctx.send("You don't have this recipe unlocked!")
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Brewing(client))