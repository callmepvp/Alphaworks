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
collections = cluster['discord']['collections']
recipes = cluster['discord']['recipes']
server = cluster['discord']['server']

recipesData = loads(Path("cogs/data/recipes/collectionRecipes.json").read_text())

class Collections(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Commands
    @commands.command(aliases = ['c', 'collection'])
    async def collections(self, ctx, mob = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        statsCollections = collections.find_one({'id' : ctx.author.id})
        statsRecipes = recipes.find_one({'id' : ctx.author.id})

        if statsGeneral is not None:
            if statsCollections is not None:
                statsServer = server.find_one({'serverID' : 0})
                regUsers = statsServer['registeredusers']
                
                text = []
                text.append("**Your Collections:**" "\n" "\n")

                count= 0
                for x in range(len(list(recipesData))):
                    leaderboard = statsGeneral['leaderboards']

                    category = list(recipesData)[x]
                    text.append(f"⇒ **{string.capwords(category)}**" f" (**#{leaderboard[count]}** :crown: out of **{regUsers}**)" "\n")
                    text.append(f"Lv **{statsCollections[str(category) + 'milestone']}** Collection: **{statsCollections[category]}**/**{statsCollections[str(category) + 'milestone']*50 + 50}** Collected" "\n")

                    #Count the recipes
                    recipesUnlocked = 0
                    for i in range(len(list(recipesData[category]))):
                        item = str(list(recipesData[category].items())[i][1])
                        if item in statsRecipes:
                            recipesUnlocked += 1

                    text.append("Recipes unlocked:" f" **{recipesUnlocked}**/**{len(list(recipesData[category]))}**")
                    if recipesUnlocked == len(list(recipesData[category])):
                        text.append(' __**MAXED**__' "\n")
                    else:
                        text.append("\n")

                    #Add the known recipes
                    counter = 0
                    for i in range(len(list(recipesData[category]))):
                        item = str(list(recipesData[category].items())[i][1])
                        if item in statsRecipes:
                            counter += 1
                            if i+1 == len(list(recipesData[category])):
                                text.append(f"`{string.capwords(item)}`")
                            else:
                                text.append(f"`{string.capwords(item)}` ; ")
                    
                    #Add the unknown recipes
                    for j in range(len(list(recipesData[category])) - counter):
                        if j+1 == len(list(recipesData[category])) - counter:
                            text.append("`???`")
                        else:
                            text.append("`???` ; ")
                    
                    text.append("\n" "\n")
                    count += 1

                await ctx.send(''.join(text))

            else:
                await ctx.send("You have no collections.")
        else:
            await ctx.send('You do not have a profile setup. Please do the setup command to make your profile!')

def setup(client):
    client.add_cog(Collections(client))