from discord.ext import commands
from pymongo import MongoClient
import discord
import random
import string

from json import loads
from pathlib import Path

#Retrieve tokens
data = loads(Path("cogs/data/tokens.json").read_text())
dbtoken = data["DATABASE_TOKEN"]
footers = loads(Path("cogs/data/footers.json").read_text())

cluster = MongoClient(dbtoken)

#Collections
general = cluster['discord']['general']
pmarket = cluster['discord']['pmarket']

#Inventory
foraging = cluster['discord']['foraging']
mining = cluster['discord']['mining']
fishing = cluster['discord']['fishing']
mobloot = cluster['discord']['mobloot']
scavenging = cluster['discord']['scavenging']
farming = cluster['discord']['farming']
potions = cluster['discord']['potions']

class PMarket(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    #Main PMarket Command
    @commands.command(aliases = ['pm'])
    async def pmarket(self, ctx, action = None, arg1 = None, arg2 = None, arg3 = None):
        statsGeneral = general.find_one({'id' : ctx.author.id})
        if statsGeneral is not None:
            
            #Default action with no arguments
            if action == None:

                #Create the market info embed
                info = []
                info.append('Welcome to the player market!' "\n"
                            "Correct usage of the command: f!pm(arket) <action> <arguments>" "\n"
                            "Use with caution: data may be lost as its still in testing." "\n" "\n"
                            "Available **actions** in the market:" "\n"
                            "`search` - Search a term on the market. **<search term>** *<category>*" "\n"
                            "`buy` - Buy an item on the market. **<search order number>** *<amount>*" "\n"
                            "`instabuy` - Instantly buys a given item for the lowest price on the market. **<item name>** *<amount>*" "\n"
                            "`info` - View the listing details about an item. **WIP**" "\n"
                            "`listings` - View your active listings." "\n"
                            "`remove` - Remove an item from your active listings. **<listing order number>**" "\n"
                            "`sell` - List an item onto the market. **<item name>** **<price>** *<amount>*" "\n" "\n"
                            "Available categories: DOESNT WORK" "\n"
                            "`tools` `weapons` `armor` `consumables` `resources`")

                embed = discord.Embed(title = 'The Player Market!', description = ''.join(info), color = 0xeab676)

                embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
                embed.set_footer(text = random.choice(list(footers['en-en'].items()))[1])
            
                await ctx.send(embed=embed)

            #Searching
            elif action == 'search':
                #f!search ITEM_NAME
                
                if arg1 != None:
                    for x in pmarket:
                        pass
            
            #Selling
            elif action == 'sell':
                if arg1 != None:
                    statsMining = mining.find_one({'id' : ctx.author.id})
                    statsForaging = foraging.find_one({'id' : ctx.author.id})
                    statsFishing = fishing.find_one({'id' : ctx.author.id})
                    statsMobLoot = mobloot.find_one({'id' : ctx.author.id})   
                    statsScavenging = scavenging.find_one({'id' : ctx.author.id})
                    statsFarming = farming.find_one({'id' : ctx.author.id})
                    statsPotions = potions.find_one({'id' : ctx.author.id})
                    #Usage: f!pmarket sell ITEM_NAME AMOUNT PRICE
                    
                    #Inventory directories to search
                    statsList = [statsMining, statsFarming, statsFishing, statsForaging, statsMobLoot, statsScavenging, statsPotions]
                    searchList = [mining, farming, fishing, foraging, mobloot, scavenging, potions]
                
                    #Search the inventory directories for the item
                    counter = 0
                    Success = False
                    for x in statsList:
                        if x == None:
                            pass
                        elif arg1 in x:
                            counter += 1
                            dataDir = x

                            cursor = statsList.index(x)
                            stat = searchList[cursor]
                    
                    #Check if the user has enough items and valid items to sell
                    if counter != 0:
                        if arg3 != None:
                            arg3 = int(arg3)
                        else:
                            arg3 = 1 #Default amount to sell if no amount is given

                        if arg3 > dataDir[arg1]:
                            Success = False
                            await ctx.send("You don't have enough items to sell.")

                        else:
                            Success = True
                    elif counter == 0:
                        Success = False
                        await ctx.send("Invalid item or invalid amount.")

                    #Check if a valid price was given
                    if arg2 != None:
                        arg2 = int(arg2)
                    else:
                        arg2 = 1 #Default price if no price was given

                    #Create the listing on the server
                    #Max 1 Listing!
                    #Hierarchy // 'listings' array > 'NAME' > 'AMOUNT' AND 'PRICE'
                    if Success:

                        #Remove the item from the inventory
                        if dataDir[arg1] - arg3 != 0:
                            stat.update_one({'id' : ctx.author.id}, {"$set":{arg1 : dataDir[arg1] - arg3}})
                        else:
                            stat.update_one({'id' : ctx.author.id}, {'$unset' : {arg1 : ''}})
                        
                        #Create the listing array for the user
                        listing = [arg1, arg2, arg3]
                        pmarket.update_one({'id' : ctx.author.id}, {"$set":{'listings' : listing}})

                        await ctx.send(f"You listed **{int(arg2)}** x **{string.capwords(arg1)}** for **{int(arg3)}** Coins!")
                else:
                    await ctx.send("You're missing one or more arguments! **(f!pm sell ITEM_NAME AMOUNT PRICE)**")
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(PMarket(client))