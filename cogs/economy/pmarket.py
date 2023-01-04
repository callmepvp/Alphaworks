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
                    message = []
                    listings = []
                    message.append(f"Searches for: `{arg1}`" "\n" "\n")

                    #Find all matching listings
                    resultsFound = 0
                    orderNr = 1
                    for x in pmarket.find(): #Iterate through all pmarket documents (Every User)
                        
                        if len(x) > 4: #Ignore users with no listings
                            listingAmount = x['listings']

                            listingCounter = 1
                            if orderNr < 10:
                                for y in range(listingAmount):
                                    if arg1 == x[f'listing{listingCounter}'][0]:

                                        #Listing Data
                                        listing = []
                                        sellerName = x['name']
                                        sellAmount = x[f'listing{listingCounter}'][1]
                                        sellPrice = x[f'listing{listingCounter}'][2]

                                        #Add the fetched listing data to an array as an array
                                        listing.append(sellerName)
                                        listing.append(sellAmount)
                                        listing.append(sellPrice)
                                        listings.append(listing)
 
                                        resultsFound += 1
                                        orderNr += 1
                                    listingCounter += 1
                            else:
                                break

                    if resultsFound != 0:
                        #Sort the array in order of growing prices (Lowest > Highest)
                        listings.sort(key=lambda x: int(x[2]))

                        #Form the final message
                        if len(listings) > 10:
                            loopAmount = 10
                        else:
                            loopAmount = len(listings)
                        
                        for j in range(loopAmount):
                            message.append(f"**{j+1}.** **{listings[j][1]}** x **{string.capwords(arg1)}** for **{listings[j][2]}** Coin ea." "\n" f"Seller: **{listings[j][0]}**" "\n \n")
                    else:
                        message.append('No results found!')

                    await ctx.send(''.join(message))
                else:
                    await ctx.send("You're missing one or more arguments! **(f!pm search ITEM_NAME)**")
            
            #Buying
            elif action == 'buy':
                #f!pm buy ITEM_NAME LISTING_ORDER_NUMBER
                pass

            elif action == 'quickbuy' or action == 'qb':
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
                        if arg2 != None:
                            arg2 = int(arg2)
                        else:
                            arg2 = 1 #Default amount to sell if no amount is given

                        if arg2 > dataDir[arg1]:
                            Success = False
                            await ctx.send("You don't have enough items to sell.")

                        else:
                            Success = True
                            #Check if a valid price was given
                            if arg3 != None:
                                arg3 = int(arg3)
                            else:
                                arg3 = 1 #Default price if no price was given

                            #Check if listings are maxed
                            listingsDir = pmarket.find_one({'id' : ctx.author.id})
                            listingNr = int(listingsDir['listings'])
                            if listingNr < 3:
                                Success = True
                            else:
                                Success = False
                                await ctx.send("You already have the maximum amount of listings! **(3)**")

                    elif counter == 0:
                        Success = False
                        await ctx.send("Invalid item or invalid amount.")

                    #Create the listing on the server
                    #Max 3 Listings! > Save amount of listed items
                    #Hierarchy // 'listings' array > 'NAME' > 'AMOUNT' AND 'PRICE'
                    if Success:

                        #Remove the item from the inventory
                        if dataDir[arg1] - arg2 != 0:
                            stat.update_one({'id' : ctx.author.id}, {"$set":{arg1 : dataDir[arg1] - arg2}})
                        else:
                            stat.update_one({'id' : ctx.author.id}, {'$unset' : {arg1 : ''}})
                        
                        #Create the listing array for the user
                        listing = [arg1, arg2, arg3]
                        pmarket.update_one({'id' : ctx.author.id}, {"$set":{f'listing{listingNr+1}' : listing}})
                        pmarket.update_one({'id' : ctx.author.id}, {"$set":{'listings' : listingsDir['listings'] + 1}})

                        await ctx.send(f"You listed **{int(arg2)}** x **{string.capwords(arg1)}** for **{int(arg3)}** Coins!")
                else:
                    await ctx.send("You're missing one or more arguments! **(f!pm sell ITEM_NAME AMOUNT PRICE)**")
        else:
            await ctx.send('You have not setup your profile yet. Please run the setup command.')

def setup(client):
    client.add_cog(PMarket(client))