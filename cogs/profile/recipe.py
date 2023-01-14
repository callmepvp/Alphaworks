import string
from discord.ext import commands
from pymongo import MongoClient

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]

cluster = MongoClient(dbtoken)

#Load all recipes
data1 = loads(Path("cogs/data/recipes/brewingRecipes.json").read_text())
data2 = loads(Path("cogs/data/recipes/cookingRecipes.json").read_text())
data3 = loads(Path("cogs/data/recipes/craftingRecipes.json").read_text())
categories = [data1, data2, data3]

general = cluster['discord']['general']
recipes = cluster['discord']['recipes']

class Recipe(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['recipe', 'r'])
    async def recipes(self, ctx, *, recipe = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            text = []
            if recipe == None:
                text.append("**Your Owned Recipes:**" "\n" "*Do f!r <recipe> for specifics!*" "\n" "\n")

                #Find the owned recipes
                document = recipes.find_one({'id' : ctx.author.id})
                for res in document:
                    val = document[res]
                    if res != 'id' and res != '_id':
                        for item in categories:
                            if res in item:

                                text.append(f"⇒ **{string.capwords(res)}**" "\n")
            else:
                counter = 0
                for item in categories:
                    if recipe in item:
                        
                        dat = item[recipe][0]
                        model = list(dat.items())
                        
                        text.append(f"⇒ **{string.capwords(recipe)}** Recipe:")
                        for i in range(int(len(model)/3)):
                            text.append("\n" f"**{model[int(len(model)/3)+i][1]}** x ") 
                            text.append(f"**{string.capwords(model[i][1])}**") 
                    else:
                        counter += 1

                if counter == 3:
                    text.append("This recipe wasn't found.")

            await ctx.send(''.join(text))

        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(Recipe(client))