import string

from discord.ext import commands
from pymongo import MongoClient

import json
from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

data = loads(Path("cogs/data/recipes/craftingRecipes.json").read_text())

#Collections
general = cluster['discord']['general']
skills = cluster['discord']['skills']
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']
items = cluster['discord']['items']
tools = cluster['discord']['tools']

foraging = cluster['discord']['foraging']
mining = cluster['discord']['mining']
mobloot = cluster['discord']['mobloot']
scavenging = cluster['discord']['scavenging']
farming = cluster['discord']['farming']

#Return the current directory
def returnDir(y, digit):
    if y["d" + str(digit)] == 'foraging':
        dir = foraging
    elif y["d" + str(digit)] == 'mining':
        dir = mining
    elif y["d" + str(digit)] == 'scavenging':
        dir = scavenging
    elif y["d" + str(digit)] == 'mobloot':
        dir = mobloot
    elif y["d" + str(digit)] == 'farming':
        dir = farming
    elif y["d" + str(digit)] == 'items':
        dir = items
    
    return dir
    
class Crafting(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command()
    async def craft(self, ctx, item, amount = 1):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            statsItems = items.find_one({'id' : ctx.author.id})
            statsSkills = skills.find_one({'id' : ctx.author.id})

            craftSuccess = False
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
                            craftSuccess = True
                            for j in range(checkedRes):
                                dir = returnDir(y, j)

                                if dir.find_one({'id' : ctx.author.id})[y[str(j)]] - amount * int(y["r" + str(j)]) != 0:
                                    dir.update_one({'id' : ctx.author.id}, {"$set":{y[str(j)] : dir.find_one({'id' : ctx.author.id})[y[str(j)]] - amount * int(y["r" + str(j)])}})
                                else:
                                    dir.update_one({'id' : ctx.author.id}, {'$unset' : {y[str(j)] : ''}})
                                    
                if craftSuccess == False:
                    await ctx.send("You don't have enough resources to craft this!")
                
                else:

                    #Give the item
                    if items.find_one({'id' : ctx.author.id, item : {'$exists': True}}) is None:
                        craftData = {
                            'id' : ctx.author.id,
                            item : amount
                        }

                        if statsItems is None:
                            items.insert_one(craftData)
                        else:
                            items.update_one({'id' : ctx.author.id}, {"$set":{item : amount}})
                    else:
                        items.update_one({'id' : ctx.author.id}, {"$set":{item : statsItems[item] + amount}})

                    await ctx.send(f'You did some crafting! You gained **{amount}** x **{string.capwords(item)}**.')

                    #Calculate the skill XP
                    existingXP = statsSkills['craftingXP']
                    existingLevel = statsSkills['craftingLevel']

                    #Calculate given XP based on ingredient amount
                    xp = 1 * amount
                    for w in range(int(len(y)/3)):
                        xp = xp * int(y["r" + str(w)])

                    craftingXP = existingXP + xp
                    
                    if craftingXP >= 50*existingLevel + 10:
                        skills.update_one({'id' : ctx.author.id}, {"$set":{'craftingXP' : 0, 'craftingLevel' : existingLevel + 1}})
                        await ctx.send(f'**[SKILL]** Your skill leveled up! You are now **Crafting** level **{existingLevel + 1}**!')

                    else:
                        skills.update_one({'id' : ctx.author.id}, {"$set":{'craftingXP' : craftingXP}})
                        await ctx.send(f'**[*]** You gained +**{xp} Crafting** XP!')
            else:
                await ctx.send("You don't have this recipe unlocked!")
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Crafting(client))